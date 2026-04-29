package com.example.skillsbot;

import dev.langchain4j.service.AiServices;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
//import dev.langchain4j.memory.chat.MessageWindowChatMemory;
//import quarkus.langchain4j.skills.Skills;
//import dev.langchain4j.Experimental.ShellSkills;
//import dev.langchain4j.skills.Skills;
import dev.langchain4j.agent.tool.Tool;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.IOException;
//import dev.langchain4j.skills.FileSystemSkillLoader;
//import java.nio.file.Path;
//import dev.langchain4j-experimental-skills-shell;
//import dev.langchain4j.langchain4j-experimental-skills-shell.ShellSkills;

//import io.quarkiverse.langchain4j.skills.SkillsSystemMessageProvider;
//import io.quarkiverse.langchain4j.RegisterAiService;

class ExtraTools {

    @Tool("Get the current time")
    public String getTime() {
        return java.time.LocalTime.now().toString();
    }

    @Tool("Write to a file using filename and content")
    public void writeFile(String filename, String content) throws IOException {
        Path baseDir = Paths.get("").toAbsolutePath().normalize();
        Path userInput = Paths.get(filename);
        Path resolved = baseDir.resolve(userInput).normalize();

        if (!resolved.startsWith(baseDir)) {
            throw new SecurityException("Access outside working directory is not allowed.");
        }
        Path path = Path.of(filename);
        Files.write(resolved, content.getBytes());
    }

    @Tool("Read file by name")
    public String readFile(String filename) throws IOException {
        Path baseDir = Paths.get("").toAbsolutePath().normalize();
        Path userInput = Paths.get(filename);
        Path resolved = baseDir.resolve(userInput).normalize();

        if (!resolved.startsWith(baseDir)) {
            throw new SecurityException("Access outside working directory is not allowed.");
        }

        return Files.readString(resolved);
    }
}

@ApplicationScoped
public class AssistantProducer {

    @Produces
    public Assistant assistant() {

        // Load all skills found in immediate subdirectories:
        //Skills skills = Skills.from(FileSystemSkillLoader.loadSkills(Path.of(".skills/skills/")));
        //ShellSkills skills = ShellSkills.from(FileSystemSkillLoader.loadSkills(Path.of(".skills/skills/")));
        //String skillsList = skills.formatAvailableSkills();
        //String sysMessage = "You are a helpful assistant who has access to the following skills:\n" + skillsList + "\nWhen the user's request relates to one of these skills, activate it first using the `activate_skill` tool before proceeding.";
        //return AiServices.create(Assistant.class);
                   //.tools(new OrderTools())
                   //.toolProvider(skills.toolProvider())
                   //.systemMessageProvider(memoryId -> "You are a helpful assistant")
                   //.systemMessageProvider(memoryId -> "You are a helpful assistant with access to a collection of skills.  When the user's request relates to one of these skills, activate it first using the `activate_skill` tool before proceeding.")
                   //.chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                   //.systemMessageProvider(memoryId -> "You are a helpful assistant")
                   //.systemMessageProvider(SkillsSystemMessageProvider.class)

        return AiServices.builder(Assistant.class)
                   .tools(new ExtraTools())
                   .build();
    }
}
