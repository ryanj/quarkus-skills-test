package com.example.skillsbot;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

import io.quarkiverse.langchain4j.skills.SkillsSystemMessageProvider;
import io.quarkiverse.langchain4j.RegisterAiService;

@RegisterAiService(systemMessageProviderSupplier = SkillsSystemMessageProvider.class)
public interface Assistant {

    String chat(@UserMessage String userMessage);
    //String chat(String message);
}
