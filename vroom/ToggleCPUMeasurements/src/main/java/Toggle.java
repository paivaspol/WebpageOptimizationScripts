import io.selendroid.client.SelendroidDriver;
import io.selendroid.client.adb.AdbConnection;
import io.selendroid.common.SelendroidCapabilities;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

/**
 * Created by vaspol on 12/13/15.
 */
public class Toggle {

    public static void main(String[] args) throws Exception {
        SelendroidDriver webDriver = new SelendroidDriver(new SelendroidCapabilities("edu.michigan.pageloadcpumeasurement:1.0"));
        System.out.println(webDriver.);
        System.out.println("here");
        webDriver.get("and-activity://edu.michigan.pageloadcpumeasurement.MainActivity");
        // WebElement element = webDriver.findElement(By.id("button"));
        // element.click();
        webDriver.backgroundApp();

    }

}
