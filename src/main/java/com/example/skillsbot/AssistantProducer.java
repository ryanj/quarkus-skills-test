package com.example.skillsbot;

import dev.langchain4j.service.AiServices;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
//import dev.langchain4j.memory.chat.MessageWindowChatMemory;

//import quarkus.langchain4j.skills.Skills;
//import dev.langchain4j.skills.Skills;
//import dev.langchain4j.skills.FileSystemSkillLoader;
//import java.nio.file.Path;

import io.quarkiverse.langchain4j.skills.SkillsSystemMessageProvider;
import io.quarkiverse.langchain4j.RegisterAiService;

@ApplicationScoped
public class AssistantProducer {

    //@RegisterAiService(systemMessageProviderSupplier = SkillsSystemMessageProvider.class)
    @Produces
    public Assistant assistant() {

        // Load all skills found in immediate subdirectories:
        //Skills skills = Skills.from(FileSystemSkillLoader.loadSkills(Path.of(".skills/skills/")));
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
                   .build();
    }
}
