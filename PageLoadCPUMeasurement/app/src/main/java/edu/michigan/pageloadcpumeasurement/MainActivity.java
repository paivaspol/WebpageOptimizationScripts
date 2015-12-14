package edu.michigan.pageloadcpumeasurement;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Environment;
import android.os.Handler;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    /**
     * The interval for executing the message in ms.
     */
    private static final int INTERVAL = 60;
    /**
     * The text when the measurement is running.
     */
    private static final String MEASUREMENT_RUNNING = "Measurement is running...";
    /**
     * The text when the measurement is not running.
     */
    private static final String MEASUREMENT_NOT_RUNNING = "Measurement is not running...";
    /**
     * The permission request constant.
     */
    private static final int PERMISSION_REQUEST = 1;

    /**
     * The handler for the event.
     */
    private Handler handler;
    private boolean startedGettingMeasurement;
    private FileOutputStream outputStream;
    private List<String> procStatLines;
    private MainActivity thisActivity;

    private BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            System.out.println("Intent: " + intent);
            Intent newIntent = new Intent(context, MainActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(newIntent);}
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        System.out.println("on create");
        System.out.println("started getting measurement: " + startedGettingMeasurement);
        setContentView(R.layout.activity_main);
        startedGettingMeasurement = false;
        handler = new Handler();
        procStatLines = new ArrayList<>();
        /* Setup the UI */
        Button measurementToggleButton = (Button) findViewById(R.id.button);
        measurementToggleButton.setOnClickListener(clickListener);
        TextView measurementStatus = (TextView) findViewById(R.id.textView);
        measurementStatus.setText(MEASUREMENT_NOT_RUNNING);
        thisActivity = this;
    }

    @Override
    public void onResume() {
        super.onResume();
        System.out.println("Resuming");
        System.out.println("Measurement State Before: " + startedGettingMeasurement);
        if (!startedGettingMeasurement) {
                    /* Check and request permission. */
            if (ContextCompat.checkSelfPermission(thisActivity, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(thisActivity, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, PERMISSION_REQUEST);
            } else {
                startCPUMeasurement();
            }
        } else {
            TextView measurementStatus = (TextView) findViewById(R.id.textView);
            handler.removeCallbacksAndMessages(null); // stop the measurement.
            measurementStatus.setText(MEASUREMENT_NOT_RUNNING);
            try {
                for (String procStatLine : procStatLines) {
                    outputStream.write(procStatLine.replace("\t", " ").getBytes());
                }
                outputStream.close();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
        startedGettingMeasurement = !startedGettingMeasurement; // Switch the flag.
        System.out.println("Measurement State After: " + startedGettingMeasurement);
        try {
            unregisterReceiver(receiver);
        } catch (IllegalArgumentException e) {

        }
    }

    @Override
    public void onPause() {
        super.onPause();
        System.out.println("Pausing");
        IntentFilter filter = new IntentFilter();
        filter.addAction(Intent.ACTION_PROCESS_TEXT);
        registerReceiver(receiver, filter);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == PERMISSION_REQUEST) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                System.out.println("Permissions granted.");
                startCPUMeasurement();
            }
        }
    }

    private View.OnClickListener clickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            if (v.getId() == R.id.button) {
                // Do nothing
            }
        }
    };

    private void startCPUMeasurement() {
        System.out.println("Starting CPU Measurement");
        TextView measurementStatus = (TextView) findViewById(R.id.textView);
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
                    //Scanner reader = new Scanner(new File("/proc/stat"));
                    // String cpuLine = reader.readLine().replace("\t", " ");
                    for (int i = 0; i < 5; i++) {
                        // Total, cpu0, cpu1, cpu2, cpu3
                        // String cpuLine = reader.nextLine();
                        String cpuLine = reader.readLine();
                        String measurementLine = currentTime + " " + cpuLine + "\n";
                        procStatLines.add(measurementLine);
                    }
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                handler.postDelayed(this, INTERVAL);
            }
        };
        runnable.run();
        measurementStatus.setText(MEASUREMENT_RUNNING);
    }

}
