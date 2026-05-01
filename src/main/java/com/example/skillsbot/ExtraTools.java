package com.example.skillsbot;

import dev.langchain4j.agent.tool.Tool;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;
import org.jboss.logging.Logger;

public class ExtraTools {

    private Logger logger = Logger.getLogger(ExtraTools.class);

    @Tool("Get the current time")
    public String getTime() {
        logger.info("@tool getTime: " + java.time.LocalTime.now().toString());
        return java.time.LocalTime.now().toString();
    }

    //@Tool("Write to a file using filename and content")
    //public void writeFile(String filename, String content) throws IOException {
    //    Path baseDir = Paths.get("").toAbsolutePath().normalize();
    //    Path userInput = Paths.get(filename);
    //    Path resolved = baseDir.resolve(userInput).normalize();
    //    logger.info("@tool writeFile: " + resolved.toString());

    //    if (!resolved.startsWith(baseDir)) {
    //        throw new SecurityException("Access outside working directory is not allowed.");
    //    }

    //    Files.write(resolved, content.getBytes());
    //}

    //@Tool("Read file by name")
    //public String readFile(String filename) throws IOException {
    //    Path baseDir = Paths.get("").toAbsolutePath().normalize();
    //    Path userInput = Paths.get(filename);
    //    Path resolved = baseDir.resolve(userInput).normalize();
    //    logger.info("@tool readFile: " + resolved.toString());

    //    if (!resolved.startsWith(baseDir)) {
    //        throw new SecurityException("Access outside working directory is not allowed.");
    //    }

    //    return Files.readString(resolved);
    //}

    //@Tool("List files within the current project using an optional relative path argument when provided")
    //public String listFileTree(String relativePath) throws IOException {
    //    Path baseDir = Paths.get("").toAbsolutePath().normalize();
    //    Path userInput = Paths.get(relativePath != null && !relativePath.isEmpty() ? relativePath : "");
    //    Path resolved = baseDir.resolve(userInput).normalize();
    //    logger.info("@tool listFileTree: " + resolved.toString());

    //    // Security check: ensure path is within project scope
    //    if (!resolved.startsWith(baseDir)) {
    //        throw new SecurityException("Access outside working directory is not allowed.");
    //    }

    //    StringBuilder tree = new StringBuilder();
    //    tree.append("File tree for: ").append(relativePath != null && !relativePath.isEmpty() ? relativePath : ".").append("\n\n");
    //    
    //    // Use a counter to limit output size
    //    int[] fileCount = {0};
    //    int maxFiles = 100;
    //    
    //    buildFileTree(resolved, tree, baseDir, fileCount, maxFiles);
    //    
    //    if (fileCount[0] >= maxFiles) {
    //        tree.append("\n... (truncated at ").append(maxFiles).append(" files)\n");
    //    }
    //    
    //    return tree.toString();
    //}

    //private void buildFileTree(Path path, StringBuilder tree, Path baseDir, int[] fileCount, int maxFiles) throws IOException {
    //    if (fileCount[0] >= maxFiles) {
    //        return; // Stop if we've hit the limit
    //    }
    //    
    //    if (!Files.exists(path)) {
    //        tree.append("Path does not exist: ").append(path).append("\n");
    //        return;
    //    }

    //    if (Files.isDirectory(path)) {
    //        // Skip common directories that can be large
    //        String dirName = path.getFileName() != null ? path.getFileName().toString() : "";
    //        if (dirName.equals("node_modules") || dirName.equals(".git") ||
    //            dirName.equals("target") || dirName.equals("build") ||
    //            dirName.equals(".idea") || dirName.equals("dist") ||
    //            dirName.equals("__pycache__") || dirName.equals(".venv")) {
    //            return;
    //        }
    //        
    //        // Recursively process directory contents, but don't list the directory itself
    //        try (var stream = Files.list(path)) {
    //            stream.sorted().forEach(p -> {
    //                try {
    //                    buildFileTree(p, tree, baseDir, fileCount, maxFiles);
    //                } catch (IOException e) {
    //                    tree.append("❌ Error reading: ").append(baseDir.relativize(p)).append("\n");
    //                }
    //            });
    //        }
    //    } else {
    //        // Show only files with full relative path
    //        tree.append(baseDir.relativize(path)).append("\n");
    //        fileCount[0]++;
    //    }
    //}
}
