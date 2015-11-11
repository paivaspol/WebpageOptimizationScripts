package edu.michigan.pageloadcpumeasurement;

import android.content.Context;
import android.os.Environment;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;

public class MainActivity extends AppCompatActivity {

    /** The interval for executing the message in ms. */
    private static final int INTERVAL = 100;
    /** The text when the measurement is running. */
    private static final String MEASUREMENT_RUNNING = "Measurement is running...";
    /** The text when the measurement is not running. */
    private static final String MEASUREMENT_NOT_RUNNING = "Measurement is not running...";

    /** The handler for the event. */
    private Handler handler;
    private boolean startedGettingMeasurement;
    private FileOutputStream outputStream;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        startedGettingMeasurement = false;
        handler = new Handler();
        /* Setup the UI */
        Button measurementToggleButton = (Button) findViewById(R.id.button);
        measurementToggleButton.setOnClickListener(clickListener);
        TextView measurementStatus = (TextView) findViewById(R.id.textView);
        measurementStatus.setText(MEASUREMENT_NOT_RUNNING);
    }

    private View.OnClickListener clickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (v.getId() == R.id.button) {
                TextView measurementStatus = (TextView) findViewById(R.id.textView);
                if (!startedGettingMeasurement) {
                    /* Setup the file output stream. */
                    File downloadFolder = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                    System.out.println("Download folder: " + downloadFolder);
                    String outputFilename = "result.txt";
                    try {
                        if (!downloadFolder.exists()) {
                            downloadFolder.mkdirs();
                        }
                        File outputFile = new File(downloadFolder, outputFilename);
                        System.out.println("Output File: " + outputFile);
                        if (outputFile.exists()) {
                            outputFile.delete();
                        }
                        outputFile.createNewFile();
                        outputStream = new FileOutputStream(outputFile);
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }

                    Runnable runnable = new Runnable() {
                        @Override
                        public void run() {
                            try {
                                long currentTime = System.currentTimeMillis();
                                BufferedReader reader = new BufferedReader(new FileReader(new File("/proc/stat")));
                                String cpuLine = reader.readLine().replace("\t", " ");
                                String measurementLine = currentTime + " " + cpuLine + "\n";
                                outputStream.write(measurementLine.getBytes());
                                outputStream.flush();
                            } catch (java.io.IOException e) {
                                throw new RuntimeException(e);
                            }
                            handler.postDelayed(this, INTERVAL);
                        }
                    };
                    runnable.run();
                    measurementStatus.setText(MEASUREMENT_RUNNING);
                } else {
                    handler.removeCallbacksAndMessages(null); // stop the measurement.
                    measurementStatus.setText(MEASUREMENT_NOT_RUNNING);
                    try {
                        outputStream.close();
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                }
                startedGettingMeasurement = !startedGettingMeasurement; // Switch the flag.
            }
        }
    };
}
