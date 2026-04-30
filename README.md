# Quarkus Skills Runner

Agentic Skills with Quarkus and LangChain4j

 * <https://quarkus.io/>
 * <https://agentskills.io/>
 * <https://docs.quarkiverse.io/quarkus-langchain4j/dev/skills.html>

## Configuration:

Export your `OPENAI_API_KEY`:

```shell
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

Optionally configure a custom `quarkus.langchain4j.openai.base-url` in `src/main/resources/application.properties`

Optionally enable ollama support in `pom.xml`

## Build and Run:

```shell script
./mvnw package && java -jar target/quarkus-app/quarkus-run.jar
```

## Basic SKILL interactions:

To test the `poem-writing` skill, enter the following command at the prompt:
```
/poem-writing
```

Conduct a security review of the codebase using the `secdevai` skills (from lola):
```shell
/secdevai review
```

Run the `/hello` skill to test a mult-step workflow:
```shell
/hello
```
