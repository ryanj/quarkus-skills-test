import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.event.Observes;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class ConfigValidator {
    
    @ConfigProperty(name = "quarkus.langchain4j.openai.api-key")
    String apiKey;
    
    void onStart(@Observes StartupEvent ev) {
        if (apiKey == null || apiKey.trim().isEmpty() || apiKey.startsWith("${")) {
            throw new IllegalStateException(
                "OPENAI_API_KEY environment variable must be set");
        }
        if (apiKey.length() < 20) {
            throw new IllegalStateException(
                "OPENAI_API_KEY appears to be invalid (too short)");
        }
    }
}