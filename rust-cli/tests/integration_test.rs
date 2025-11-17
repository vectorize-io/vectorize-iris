use std::process::Command;
use std::path::PathBuf;

fn get_test_file() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("../examples/sample.md");
    path
}

fn get_binary_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("target/debug/vectorize-iris");
    path
}

#[test]
fn test_cli_help() {
    let output = Command::new(get_binary_path())
        .arg("--help")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("Extract text from files using Vectorize Iris"));
}

#[test]
fn test_cli_version() {
    let output = Command::new(get_binary_path())
        .arg("--version")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success());
}

#[test]
#[ignore] // This test requires API credentials and network access
fn test_cli_extraction_json() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("-o")
        .arg("json")
        .output()
        .expect("Failed to execute command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Command failed: {}", stderr);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);

    // Validate JSON output
    let json: serde_json::Value = serde_json::from_str(&stdout)
        .expect("Output should be valid JSON");

    assert!(json.get("success").is_some());
    assert!(json.get("text").is_some() || json.get("chunks").is_some());
}

#[test]
#[ignore] // This test requires API credentials and network access
fn test_cli_extraction_yaml() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("-o")
        .arg("yaml")
        .output()
        .expect("Failed to execute command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Command failed: {}", stderr);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);

    // Validate YAML output
    let yaml: serde_yaml::Value = serde_yaml::from_str(&stdout)
        .expect("Output should be valid YAML");

    assert!(yaml.get("success").is_some());
}

#[test]
#[ignore] // This test requires API credentials and network access
fn test_cli_extraction_pretty() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("-o")
        .arg("pretty")
        .output()
        .expect("Failed to execute command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Command failed: {}", stderr);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(!stdout.is_empty());
}

#[test]
#[ignore] // This test requires API credentials and network access
fn test_cli_with_chunking() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("--chunking-strategy")
        .arg("markdown")
        .arg("--chunk-size")
        .arg("512")
        .arg("-o")
        .arg("json")
        .output()
        .expect("Failed to execute command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Command failed: {}", stderr);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let json: serde_json::Value = serde_json::from_str(&stdout)
        .expect("Output should be valid JSON");

    // When chunking is requested, chunks should be present
    assert!(json.get("chunks").is_some());
    if let Some(chunks) = json.get("chunks").and_then(|c| c.as_array()) {
        assert!(!chunks.is_empty(), "Should have at least one chunk");
    }
}

#[test]
#[ignore] // This test requires API credentials and network access
fn test_cli_with_metadata() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("--metadata-schema")
        .arg("doc-info:Extract title, author, and main topics")
        .arg("-o")
        .arg("json")
        .output()
        .expect("Failed to execute command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Command failed: {}", stderr);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let json: serde_json::Value = serde_json::from_str(&stdout)
        .expect("Output should be valid JSON");

    // Metadata field should be present (even if null)
    assert!(json.get("metadata").is_some());
}

#[test]
#[ignore] // This test requires API credentials and network access
fn test_cli_with_parsing_instructions() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("--parsing-instructions")
        .arg("Focus on extracting code examples")
        .arg("-o")
        .arg("json")
        .output()
        .expect("Failed to execute command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Command failed: {}", stderr);
    }

    assert!(output.status.success());
}

#[test]
fn test_cli_missing_file() {
    let output = Command::new(get_binary_path())
        .arg("nonexistent.pdf")
        .output()
        .expect("Failed to execute command");

    assert!(!output.status.success());
    // CLI should fail when file doesn't exist
}

#[test]
fn test_cli_invalid_output_format() {
    let output = Command::new(get_binary_path())
        .arg(get_test_file())
        .arg("-o")
        .arg("invalid")
        .output()
        .expect("Failed to execute command");

    assert!(!output.status.success());
}
