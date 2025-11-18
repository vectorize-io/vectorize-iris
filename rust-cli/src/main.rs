use anyhow::{Context, Result, anyhow};
use clap::{Parser, ValueEnum};
use console::{style, Emoji};
use indicatif::{ProgressBar, ProgressStyle, MultiProgress};
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::path::PathBuf;
use std::thread;
use std::time::Duration;
use textwrap::{wrap, Options};
use tempfile::NamedTempFile;

// Emojis for beautiful output
static SPARKLE: Emoji = Emoji("✨", "");
static ROCKET: Emoji = Emoji("🚀", ">");
static PACKAGE: Emoji = Emoji("📦", "*");
static GEAR: Emoji = Emoji("⚙️ ", "");
static CHECK: Emoji = Emoji("✓", "+");
static CROSS: Emoji = Emoji("✗", "x");
static HOURGLASS: Emoji = Emoji("⏳", ".");
static DOC: Emoji = Emoji("📄", "#");
static BULB: Emoji = Emoji("💡", "!");
static CHART: Emoji = Emoji("📊", "=");

#[derive(Parser)]
#[command(name = "vectorize-iris")]
#[command(about = "Extract text from files using Vectorize Iris", long_about = None)]
#[command(version)]
struct Cli {
    /// Path or URL to the file to extract text from
    #[arg(value_name = "FILE")]
    file_path: String,

    /// API token (defaults to VECTORIZE_API_TOKEN env var)
    #[arg(long)]
    api_token: Option<String>,

    /// Organization ID (defaults to VECTORIZE_ORG_ID env var)
    #[arg(long)]
    org_id: Option<String>,

    /// Output format (pretty: styled output, json: JSON format, yaml: YAML format, text: plain text only)
    #[arg(short = 'o', long, value_enum, default_value = "pretty")]
    output: OutputFormat,

    /// Output file path (writes to file instead of stdout)
    #[arg(short = 'f', long, value_name = "FILE")]
    output_file: Option<PathBuf>,

    /// Chunk size (default: 256)
    #[arg(long)]
    chunk_size: Option<u32>,

    /// Metadata schema (format: id:JSON_VALUE, can be repeated). JSON_VALUE must be valid JSON and will be wrapped in a 'document' key if not already wrapped. When provided, infer-metadata-schema is automatically set to false.
    #[arg(long = "metadata-schema", value_name = "ID:JSON")]
    metadata_schemas: Vec<String>,

    /// Infer metadata schema automatically (default: true, automatically false if --metadata-schema is provided)
    #[arg(long, default_value = "true", action = clap::ArgAction::Set)]
    infer_metadata_schema: bool,

    /// Parsing instructions for the AI model
    #[arg(long)]
    parsing_instructions: Option<String>,

    /// Seconds between status checks
    #[arg(long, default_value = "2")]
    poll_interval: u64,

    /// Maximum seconds to wait for extraction
    #[arg(long, default_value = "300")]
    timeout: u64,

    /// Show detailed request/response information
    #[arg(long, short = 'v')]
    verbose: bool,
}

#[derive(Clone, ValueEnum)]
enum OutputFormat {
    Pretty,
    Json,
    Yaml,
    Text,
}

// Request/Response Models

#[derive(Serialize)]
struct StartUploadRequest {
    name: String,
    #[serde(rename = "contentType")]
    content_type: String,
}

#[derive(Deserialize)]
struct StartUploadResponse {
    #[serde(rename = "fileId")]
    file_id: String,
    #[serde(rename = "uploadUrl")]
    upload_url: String,
}

#[derive(Serialize)]
struct MetadataSchema {
    id: String,
    schema: String,
}

#[derive(Serialize)]
struct MetadataStrategy {
    #[serde(skip_serializing_if = "Option::is_none")]
    schemas: Option<Vec<MetadataSchema>>,
    #[serde(skip_serializing_if = "Option::is_none", rename = "inferSchema")]
    infer_schema: Option<bool>,
}

#[derive(Serialize)]
struct StartExtractionRequest {
    #[serde(rename = "fileId")]
    file_id: String,
    #[serde(skip_serializing_if = "Option::is_none", rename = "type")]
    extraction_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none", rename = "chunkSize")]
    chunk_size: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    metadata: Option<MetadataStrategy>,
    #[serde(skip_serializing_if = "Option::is_none", rename = "parsingInstructions")]
    parsing_instructions: Option<String>,
}

#[derive(Deserialize)]
struct StartExtractionResponse {
    #[serde(rename = "extractionId")]
    extraction_id: String,
}

#[derive(Deserialize, Serialize)]
struct ExtractionResultData {
    success: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    chunks: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    text: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    metadata: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none", rename = "metadataSchema")]
    metadata_schema: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none", rename = "chunksMetadata")]
    chunks_metadata: Option<Vec<Option<String>>>,
    #[serde(skip_serializing_if = "Option::is_none", rename = "chunksSchema")]
    chunks_schema: Option<Vec<Option<String>>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
}

#[derive(Deserialize)]
struct ExtractionResult {
    ready: bool,
    data: Option<ExtractionResultData>,
}

fn create_spinner(msg: &str) -> ProgressBar {
    let pb = ProgressBar::new_spinner();
    pb.set_style(
        ProgressStyle::default_spinner()
            .tick_strings(&["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
            .template("{spinner:.cyan} {msg}")
            .unwrap(),
    );
    pb.set_message(msg.to_string());
    pb.enable_steady_tick(Duration::from_millis(80));
    pb
}

fn is_url(path: &str) -> bool {
    path.starts_with("http://") || path.starts_with("https://")
}

fn download_url(url: &str) -> Result<NamedTempFile> {
    eprintln!();
    eprintln!("{} {}", ROCKET, style("Downloading file from URL").cyan().bold());
    eprintln!("{}", style("─".repeat(50)).dim());
    eprintln!();

    let client = Client::new();
    let response = client
        .get(url)
        .send()
        .context("Failed to download file from URL")?;

    if !response.status().is_success() {
        return Err(anyhow!(
            "Failed to download file: HTTP {}",
            response.status()
        ));
    }

    let mut temp_file = NamedTempFile::new()
        .context("Failed to create temporary file")?;

    let bytes = response.bytes()
        .context("Failed to read response body")?;

    std::io::Write::write_all(&mut temp_file, &bytes)
        .context("Failed to write to temporary file")?;

    eprintln!("{} Downloaded {} bytes to temporary file", CHECK, style(format_bytes(bytes.len() as u64)).cyan());
    eprintln!();

    Ok(temp_file)
}

fn process_directory(
    dir_path: &PathBuf,
    api_token: &str,
    org_id: &str,
    output_format: &OutputFormat,
    output_dir: Option<&PathBuf>,
    chunk_size: Option<u32>,
    metadata_schemas: Vec<String>,
    infer_metadata_schema: bool,
    parsing_instructions: Option<String>,
    poll_interval: u64,
    timeout: u64,
    verbose: bool,
) -> Result<()> {
    eprintln!();
    eprintln!("{} {}", PACKAGE, style("Processing Directory").cyan().bold());
    eprintln!("{}", style("─".repeat(50)).dim());
    eprintln!();

    // Collect all files in directory
    let entries: Vec<_> = fs::read_dir(dir_path)?
        .filter_map(|e| e.ok())
        .filter(|e| e.path().is_file())
        .collect();

    if entries.is_empty() {
        eprintln!("{} No files found in directory", CROSS);
        return Ok(());
    }

    eprintln!("{} Found {} files to process", BULB, style(entries.len()).cyan().bold());
    eprintln!();

    // Create output directory if needed
    let output_path = if let Some(out_dir) = output_dir {
        fs::create_dir_all(out_dir)
            .context(format!("Failed to create output directory: {}", out_dir.display()))?;
        Some(out_dir.clone())
    } else {
        None
    };

    let has_schemas = !metadata_schemas.is_empty() || infer_metadata_schema;
    let mut successful = 0;
    let mut failed = 0;

    // Process each file
    for (idx, entry) in entries.iter().enumerate() {
        let file_path = entry.path();
        let file_name = file_path.file_name().unwrap().to_string_lossy();

        eprintln!();
        eprintln!("{} {} {}/{} - {}",
            GEAR,
            style("Processing").cyan(),
            style(idx + 1).bold(),
            style(entries.len()).bold(),
            style(&file_name).yellow()
        );

        match extract_text(
            &file_path,
            api_token,
            org_id,
            chunk_size,
            metadata_schemas.clone(),
            infer_metadata_schema,
            parsing_instructions.clone(),
            poll_interval,
            timeout,
            verbose,
        ) {
            Ok(result) => {
                // Determine output file path
                let out_file = if let Some(ref out_path) = output_path {
                    let base_name = file_path.file_stem().unwrap().to_string_lossy();
                    let extension = match output_format {
                        OutputFormat::Json => "json",
                        OutputFormat::Yaml => "yaml",
                        OutputFormat::Text => "txt",
                        OutputFormat::Pretty => "txt",
                    };
                    Some(out_path.join(format!("{}.{}", base_name, extension)))
                } else {
                    None
                };

                if let Err(e) = format_output(&result, output_format, has_schemas, out_file.as_ref()) {
                    eprintln!("{} Failed to write output: {}", CROSS, e);
                    failed += 1;
                } else {
                    successful += 1;
                }
            }
            Err(e) => {
                eprintln!("{} Extraction failed: {}", CROSS, style(&e.to_string()).red());
                failed += 1;
            }
        }
    }

    eprintln!();
    eprintln!("{}", style("─".repeat(50)).dim());
    eprintln!("{} {}", SPARKLE, style("Batch Processing Complete").green().bold());
    eprintln!();
    eprintln!("  {} Successful: {}", CHECK, style(successful).green().bold());
    if failed > 0 {
        eprintln!("  {} Failed: {}", CROSS, style(failed).red().bold());
    }
    eprintln!();

    Ok(())
}

fn extract_text(
    file_path: &PathBuf,
    api_token: &str,
    org_id: &str,
    chunk_size: Option<u32>,
    metadata_schemas: Vec<String>,
    infer_metadata_schema: bool,
    parsing_instructions: Option<String>,
    poll_interval: u64,
    timeout: u64,
    verbose: bool,
) -> Result<ExtractionResultData> {
    let multi = MultiProgress::new();

    // Print header (to stderr so it doesn't contaminate output)
    eprintln!();
    eprintln!("{} {}", SPARKLE, style("Vectorize Iris Extraction").cyan().bold());
    eprintln!("{}", style("─".repeat(50)).dim());
    eprintln!();

    // Validate file exists
    if !file_path.exists() {
        return Err(anyhow!("File not found: {}", file_path.display()));
    }

    let base_url = format!("https://api.vectorize.io/v1/org/{}", org_id);
    let client = Client::new();

    let file_name = file_path
        .file_name()
        .context("Invalid file name")?
        .to_string_lossy()
        .to_string();

    let file_metadata = fs::metadata(file_path)?;
    let file_size = file_metadata.len();

    // Step 1: Start file upload
    let upload_spinner = multi.add(create_spinner(&format!(
        "{} Preparing upload for {} ({} bytes)",
        PACKAGE, style(&file_name).yellow(),
        style(format_bytes(file_size)).cyan()
    )));

    let upload_request = StartUploadRequest {
        name: file_name.clone(),
        content_type: "application/octet-stream".to_string(),
    };

    let request_body = serde_json::to_string_pretty(&upload_request).unwrap();
    let request_url = format!("{}/files", base_url);

    let request_builder = client
        .post(&request_url)
        .header("Authorization", format!("Bearer {}", api_token))
        .header("Content-Type", "application/json")
        .json(&upload_request);

    if verbose {
        let headers = request_builder.try_clone()
            .unwrap()
            .build()?
            .headers()
            .clone();
        log_request("POST", &request_url, &headers, Some(&request_body));
    }

    let upload_response = request_builder
        .send()
        .context("Failed to start upload")?;

    let response_status = upload_response.status();
    let response_headers = upload_response.headers().clone();
    let response_text = upload_response.text()?;

    if verbose {
        log_response(&response_status, &response_headers, &response_text);
    }

    if !response_status.is_success() {
        upload_spinner.finish_with_message(format!("{} Upload failed", CROSS));
        return Err(anyhow!(
            "Failed to start upload: {} - {}",
            response_status,
            response_text
        ));
    }

    let upload_data: StartUploadResponse = serde_json::from_str(&response_text)?;
    upload_spinner.finish_with_message(format!("{} Upload prepared", CHECK));

    // Step 2: Upload file
    let file_spinner = multi.add(create_spinner(&format!("{} Uploading file content", ROCKET)));

    let file_content = fs::read(file_path)?;

    let put_request_builder = client
        .put(&upload_data.upload_url)
        .header("Content-Type", "application/octet-stream")
        .header("Content-Length", file_size.to_string())
        .body(file_content);

    if verbose {
        let headers = put_request_builder.try_clone()
            .unwrap()
            .build()?
            .headers()
            .clone();
        log_request("PUT", &upload_data.upload_url, &headers, Some(&format!("<binary data: {} bytes>", file_size)));
    }

    let put_response = put_request_builder
        .send()
        .context("Failed to upload file")?;

    let put_status = put_response.status();
    let put_headers = put_response.headers().clone();
    let put_text = put_response.text()?;

    if verbose {
        log_response(&put_status, &put_headers, &put_text);
    }

    if !put_status.is_success() {
        file_spinner.finish_with_message(format!("{} File upload failed", CROSS));
        return Err(anyhow!(
            "Failed to upload file: {} - {}",
            put_status,
            put_text
        ));
    }

    file_spinner.finish_with_message(format!("{} File uploaded successfully", CHECK));

    // Step 3: Start extraction
    let extract_spinner = multi.add(create_spinner(&format!("{} Starting extraction", GEAR)));

    // Parse metadata schemas
    let parsed_schemas: Option<Vec<MetadataSchema>> = if !metadata_schemas.is_empty() {
        let schemas: Result<Vec<MetadataSchema>> = metadata_schemas
            .iter()
            .map(|s| {
                let parts: Vec<&str> = s.splitn(2, ':').collect();
                if parts.len() != 2 {
                    return Err(anyhow!("Invalid metadata schema format: {}. Expected ID:JSON", s));
                }

                let id = parts[0].to_string();
                let value_str = parts[1];

                // Parse as JSON to validate
                let json_value: serde_json::Value = serde_json::from_str(value_str)
                    .context(format!("Invalid JSON in metadata schema '{}': {}", id, value_str))?;

                // Check if it's already wrapped in a 'document' key
                let schema_value = if json_value.is_object() && json_value.get("document").is_some() {
                    // Already wrapped, use as-is
                    json_value
                } else {
                    // Wrap in 'document' key
                    serde_json::json!({
                        "document": json_value
                    })
                };

                Ok(MetadataSchema {
                    id,
                    schema: schema_value.to_string(),
                })
            })
            .collect();
        Some(schemas?)
    } else {
        None
    };

    // Always create metadata with inferSchema defaulting to true
    let metadata = if parsed_schemas.is_some() || infer_metadata_schema {
        Some(MetadataStrategy {
            schemas: parsed_schemas,
            infer_schema: Some(infer_metadata_schema),
        })
    } else {
        None
    };

    let extraction_request = StartExtractionRequest {
        file_id: upload_data.file_id,
        extraction_type: Some("iris".to_string()),
        chunk_size,
        metadata,
        parsing_instructions,
    };

    let extraction_body = serde_json::to_string_pretty(&extraction_request).unwrap();
    let extraction_url = format!("{}/extraction", base_url);

    let extraction_request_builder = client
        .post(&extraction_url)
        .header("Authorization", format!("Bearer {}", api_token))
        .header("Content-Type", "application/json")
        .json(&extraction_request);

    if verbose {
        let headers = extraction_request_builder.try_clone()
            .unwrap()
            .build()?
            .headers()
            .clone();
        log_request("POST", &extraction_url, &headers, Some(&extraction_body));
    }

    let extraction_response = extraction_request_builder
        .send()
        .context("Failed to start extraction")?;

    let extraction_status = extraction_response.status();
    let extraction_headers = extraction_response.headers().clone();
    let extraction_text = extraction_response.text()?;

    if verbose {
        log_response(&extraction_status, &extraction_headers, &extraction_text);
    }

    if !extraction_status.is_success() {
        extract_spinner.finish_with_message(format!("{} Extraction failed to start", CROSS));
        return Err(anyhow!(
            "Failed to start extraction: {} - {}",
            extraction_status,
            extraction_text
        ));
    }

    let extraction_data: StartExtractionResponse = serde_json::from_str(&extraction_text)?;
    extract_spinner.finish_with_message(format!("{} Extraction started", CHECK));

    // Step 4: Poll for completion
    let poll_spinner = multi.add(create_spinner(&format!("{} Processing document", HOURGLASS)));

    let start_time = std::time::Instant::now();
    let timeout_duration = Duration::from_secs(timeout);
    let poll_duration = Duration::from_secs(poll_interval);

    let mut poll_count = 0;
    loop {
        if start_time.elapsed() > timeout_duration {
            poll_spinner.finish_with_message(format!("{} Extraction timed out", CROSS));
            return Err(anyhow!("Extraction timed out after {} seconds", timeout));
        }

        poll_count += 1;
        let elapsed = start_time.elapsed().as_secs();
        poll_spinner.set_message(format!(
            "{} Processing document ({}s elapsed, check #{})",
            HOURGLASS,
            elapsed,
            poll_count
        ));

        let status_url = format!("{}/extraction/{}", base_url, extraction_data.extraction_id);
        let status_request_builder = client
            .get(&status_url)
            .header("Authorization", format!("Bearer {}", api_token));

        if verbose {
            let headers = status_request_builder.try_clone()
                .unwrap()
                .build()?
                .headers()
                .clone();
            log_request("GET", &status_url, &headers, None);
        }

        let status_response = status_request_builder
            .send()
            .context("Failed to check status")?;

        let status_response_status = status_response.status();
        let status_response_headers = status_response.headers().clone();
        let status_response_text = status_response.text()?;

        if verbose {
            log_response(&status_response_status, &status_response_headers, &status_response_text);
        }

        if !status_response_status.is_success() {
            poll_spinner.finish_with_message(format!("{} Status check failed", CROSS));
            return Err(anyhow!(
                "Failed to check status: {} - {}",
                status_response_status,
                status_response_text
            ));
        }

        let result: ExtractionResult = serde_json::from_str(&status_response_text)?;

        if result.ready {
            poll_spinner.finish_with_message(format!("{} Extraction completed in {}s", CHECK, elapsed));

            let data = result.data.context("No data in extraction result")?;

            if !data.success {
                let error_msg = data.error.unwrap_or_else(|| "Unknown error".to_string());
                return Err(anyhow!("Extraction failed: {}", error_msg));
            }

            println!();
            return Ok(data);
        }

        thread::sleep(poll_duration);
    }
}

fn format_bytes(bytes: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB"];
    let mut size = bytes as f64;
    let mut unit_idx = 0;

    while size >= 1024.0 && unit_idx < UNITS.len() - 1 {
        size /= 1024.0;
        unit_idx += 1;
    }

    format!("{:.1} {}", size, UNITS[unit_idx])
}

fn log_request(method: &str, url: &str, headers: &reqwest::header::HeaderMap, body: Option<&str>) {
    eprintln!();
    eprintln!("{}", style("━".repeat(70)).dim());
    eprintln!("{} {} {}", style("→").cyan().bold(), style(method).green().bold(), style(url).yellow());
    eprintln!("{}", style("━".repeat(70)).dim());
    eprintln!();
    eprintln!("{}", style("Headers:").cyan().bold());
    for (key, value) in headers.iter() {
        let value_str = if key == "authorization" {
            "Bearer ***REDACTED***".to_string()
        } else {
            value.to_str().unwrap_or("<non-utf8>").to_string()
        };
        eprintln!("  {}: {}", style(key.as_str()).dim(), value_str);
    }
    if let Some(body_content) = body {
        eprintln!();
        eprintln!("{}", style("Body:").cyan().bold());
        eprintln!("{}", body_content);
    }
    eprintln!();
}

fn log_response(status: &reqwest::StatusCode, headers: &reqwest::header::HeaderMap, body: &str) {
    eprintln!("{}", style("━".repeat(70)).dim());
    eprintln!("{} {} {}",
        style("←").cyan().bold(),
        if status.is_success() {
            style("Response").green().bold()
        } else {
            style("Response").red().bold()
        },
        if status.is_success() {
            style(status.as_str()).green()
        } else {
            style(status.as_str()).red()
        }
    );
    eprintln!("{}", style("━".repeat(70)).dim());
    eprintln!();
    eprintln!("{}", style("Headers:").cyan().bold());
    for (key, value) in headers.iter() {
        eprintln!("  {}: {}", style(key.as_str()).dim(), value.to_str().unwrap_or("<non-utf8>"));
    }
    eprintln!();
    eprintln!("{}", style("Body:").cyan().bold());
    eprintln!("{}", body);
    eprintln!();
}

fn print_section_header(title: &str, emoji: Emoji) {
    println!();
    println!("{}", style("─".repeat(60)).dim());
    println!("{} {}", emoji, style(title).cyan().bold());
    println!("{}", style("─".repeat(60)).dim());
    println!();
}

fn print_wrapped_text(text: &str, indent: usize) {
    let terminal_width = console::Term::stdout().size().1 as usize;
    let wrap_width = terminal_width.min(100) - indent;

    let indent_str = " ".repeat(indent);
    let options = Options::new(wrap_width)
        .initial_indent(&indent_str)
        .subsequent_indent(&indent_str);

    for line in text.lines() {
        for wrapped_line in wrap(line, &options) {
            println!("{}", wrapped_line);
        }
    }
}

fn write_output(content: String, output_file: Option<&PathBuf>) -> Result<()> {
    if let Some(path) = output_file {
        fs::write(path, content)
            .context(format!("Failed to write to file: {}", path.display()))?;
        eprintln!("{} Output written to {}", CHECK, style(path.display()).cyan());
    } else {
        print!("{}", content);
    }
    Ok(())
}

fn format_output(data: &ExtractionResultData, format: &OutputFormat, has_schemas: bool, output_file: Option<&PathBuf>) -> Result<()> {
    match format {
        OutputFormat::Json => {
            let json = serde_json::to_string_pretty(data).unwrap();
            write_output(json, output_file)?;
        }
        OutputFormat::Yaml => {
            let yaml = serde_yaml::to_string(data).unwrap();
            write_output(yaml, output_file)?;
        }
        OutputFormat::Text => {
            // Only print the extracted text, nothing else
            if let Some(text) = &data.text {
                write_output(text.clone(), output_file)?;
            }
        }
        OutputFormat::Pretty => {
            // Pretty format with beautiful styling

            // Show chunks if available
            if data.chunks.is_some() && data.chunks.as_ref().unwrap().len() > 0 {
                let chunks = data.chunks.as_ref().unwrap();

                print_section_header(
                    &format!("Document Chunks ({} total)", chunks.len()),
                    CHART
                );

                for (i, chunk) in chunks.iter().enumerate() {
                    println!("{} {}",
                        style(format!("Chunk {}", i + 1)).bold().yellow(),
                        style(format!("({} chars)", chunk.len())).dim()
                    );
                    println!();
                    print_wrapped_text(chunk, 2);

                    // Print chunk metadata if available
                    if let Some(chunks_metadata) = &data.chunks_metadata {
                        if i < chunks_metadata.len() {
                            if let Some(metadata) = &chunks_metadata[i] {
                                println!();
                                println!("  {} {}",
                                    style("Metadata:").dim(),
                                    style(metadata).cyan()
                                );
                            }
                        }
                    }

                    if i < chunks.len() - 1 {
                        println!();
                        println!("{}", style("  ⋯").dim());
                        println!();
                    }
                }
            }

            // Show metadata if available and explicitly requested
            if has_schemas && data.metadata.is_some() {
                print_section_header("Document Metadata", BULB);

                if let Ok(metadata) = serde_json::from_str::<serde_json::Value>(data.metadata.as_ref().unwrap()) {
                    println!("{}", serde_json::to_string_pretty(&metadata).unwrap());
                } else {
                    println!("{}", data.metadata.as_ref().unwrap());
                }

                if let Some(schema) = &data.metadata_schema {
                    println!();
                    println!("{} {}",
                        style("Schema:").dim(),
                        style(schema).cyan()
                    );
                }
            }

            // Always show full text if available
            if let Some(text) = &data.text {
                print_section_header("Extracted Text", DOC);

                let char_count = text.chars().count();
                let word_count = text.split_whitespace().count();
                let line_count = text.lines().count();

                println!("{} {} {} {} {} {}",
                    style("Stats:").dim(),
                    style(format!("{} chars", char_count)).cyan(),
                    style("•").dim(),
                    style(format!("{} words", word_count)).cyan(),
                    style("•").dim(),
                    style(format!("{} lines", line_count)).cyan()
                );
                println!();
                print_wrapped_text(text, 0);
            }

            println!();
            println!("{}", style("─".repeat(60)).dim());
            println!("{} {}", SPARKLE, style("Extraction complete!").green().bold());

            if output_file.is_some() {
                eprintln!();
                eprintln!("{} Note: Pretty format output is not saved to file. Use -o json/yaml/text for file output.",
                    style("ℹ").cyan());
            }

            println!();
        }
    }
    Ok(())
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    // Get credentials from args or environment
    let api_token = cli.api_token
        .or_else(|| env::var("VECTORIZE_API_TOKEN").ok())
        .context(
            "Missing API token. Set VECTORIZE_API_TOKEN env var or use --api-token flag",
        )?;

    let org_id = cli.org_id
        .or_else(|| env::var("VECTORIZE_ORG_ID").ok())
        .context("Missing org ID. Set VECTORIZE_ORG_ID env var or use --org-id flag")?;

    // Automatically set infer_metadata_schema to false if metadata schemas are provided
    let infer_metadata_schema = if !cli.metadata_schemas.is_empty() {
        false
    } else {
        cli.infer_metadata_schema
    };

    // Handle URL, directory, or local file path
    let _temp_file; // Keep temp file alive until end of function
    let file_path: PathBuf = if is_url(&cli.file_path) {
        _temp_file = download_url(&cli.file_path)?;
        _temp_file.path().to_path_buf()
    } else {
        PathBuf::from(&cli.file_path)
    };

    // Check if input is a directory
    if file_path.is_dir() {
        // Process all files in directory
        return process_directory(
            &file_path,
            &api_token,
            &org_id,
            &cli.output,
            cli.output_file.as_ref(),
            cli.chunk_size,
            cli.metadata_schemas,
            infer_metadata_schema,
            cli.parsing_instructions,
            cli.poll_interval,
            cli.timeout,
            cli.verbose,
        );
    }

    // Extract text from single file
    let has_schemas = !cli.metadata_schemas.is_empty() || infer_metadata_schema;

    let result = extract_text(
        &file_path,
        &api_token,
        &org_id,
        cli.chunk_size,
        cli.metadata_schemas,
        infer_metadata_schema,
        cli.parsing_instructions,
        cli.poll_interval,
        cli.timeout,
        cli.verbose,
    )?;

    // Format and print output
    format_output(&result, &cli.output, has_schemas, cli.output_file.as_ref())?;

    Ok(())
}
