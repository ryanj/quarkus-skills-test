package com.example.skillsbot;

import io.quarkus.runtime.QuarkusApplication;
import io.quarkus.runtime.annotations.QuarkusMain;
import io.smallrye.common.annotation.Blocking;
import jakarta.inject.Inject;
import java.util.Scanner;

@QuarkusMain
public class SkillsBotApp implements QuarkusApplication {

    @Inject
    Assistant assistant;

    @Override
    public int run(String... args) {
        String[] welcomeTo = {
            "",
            "███████╗██╗  ██╗██╗██║     ██╗     ███████╗",
            "██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝",
            "███████╗█████╔╝ ██║██║     ██║     ███████╗",
            "╚════██║██╔═██╗ ██║██║     ██║     ╚════██║",
            "███████║██║  ██╗██║███████╗███████╗███████║",
            "╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝",
            "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
            "",
            "██████╗ ██╗   ██╗███╗   ██╗███╗   ██╗███████╗██████╗ ",
            "██╔══██╗██║   ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗",
            "██████╔╝██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝",
            "██╔══██╗██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗",
            "██║  ██║╚██████╔╝██║ ╚████║██║ ╚████║███████╗██║  ██║",
            "╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝",
            "▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀"
        };
        for (String line : welcomeTo ) {
            System.out.println(line);
        }
        System.out.println("Chatbot started (type 'exit' to quit)");

        try (Scanner scanner = new Scanner(System.in)) {
            while (true) {
                System.out.print("> ");

                //clean the input
                String inputRaw = scanner.nextLine();
                String input = inputRaw.replaceAll("[\\p{Cntrl}&&[^\n\t]]", "");

                // Skip empty lines
                if (input == null || input.trim().isEmpty()) {
                    continue;
                }

                // Limit input to 10000 characters max
                if (input.length() > 10000) {
                    System.out.println("Input exceeds 10000 char limit. Please try again.");
                    continue;
                }

                // Use "exit" or CTRL-D to quit
                if ("exit".equalsIgnoreCase(input) || (!input.isEmpty() && input.charAt(0) == 4) ) {
                    break;
                }

                // Process chat input and print the response
                String response = assistant.chat(input);
                System.out.println(response);
            }

        }catch (Exception e) {
            //e.printStackTrace();
            String errMsg = e.getMessage();
            // Ignore errors related to empty input
            if (!errMsg.equals("No line found")) {
                System.err.println("Error: " + errMsg + "\n");
            }
        }
        return 0;
    }
}