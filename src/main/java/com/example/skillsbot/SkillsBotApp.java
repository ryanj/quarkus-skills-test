package com.example.skillsbot;

import io.quarkus.runtime.QuarkusApplication;
import io.quarkus.runtime.annotations.QuarkusMain;

import jakarta.inject.Inject;
import java.util.Scanner;

@QuarkusMain
public class SkillsBotApp implements QuarkusApplication {

    @Inject
    Assistant assistant;

    @Override
    public int run(String... args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Chatbot started (type 'exit' to quit)");

        while (true) {
            System.out.print("> ");
            String input = scanner.nextLine();

            if (input == null || input.trim().isEmpty()) {
                continue;
            }

            if ("exit".equalsIgnoreCase(input)) {
                break;
            }

            String response = assistant.chat(input);
            System.out.println(response);
        }

        return 0;
    }
}
