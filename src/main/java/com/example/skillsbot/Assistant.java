package com.example.skillsbot;

import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

public interface Assistant {

    //TODO: Read from AGENT.md when available
    //@SystemMessage("You are a helpful assistant who has access to the following skills:\n" + skills.formatAvailableSkills() + "\nWhen the user's request relates to one of these skills, activate it first using the `activate_skill` tool before proceeding.")
    //@SystemMessage(sysMessage)
    @SystemMessage("You are a helpful assistant")
    String chat(@UserMessage String userMessage);
}
