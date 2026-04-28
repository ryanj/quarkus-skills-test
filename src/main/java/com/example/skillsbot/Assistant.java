package com.example.skillsbot;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

import io.quarkiverse.langchain4j.skills.SkillsSystemMessageProvider;
import io.quarkiverse.langchain4j.RegisterAiService;

@RegisterAiService(systemMessageProviderSupplier = SkillsSystemMessageProvider.class)
public interface Assistant {

    //TODO: Read from AGENT.md when available
    //@SystemMessage("You are a helpful assistant who has access to the following skills:\n" + skills.formatAvailableSkills() + "\nWhen the user's request relates to one of these skills, activate it first using the `activate_skill` tool before proceeding.")
    //@SystemMessage(sysMessage)
    //@SystemMessage("You are a helpful assistant with access to a collection of skills.  When the user's request relates to one of these skills, activate it first using the `activate_skill` tool before proceeding.")
    String chat(@UserMessage String userMessage);
    //String chat(String message);
}
