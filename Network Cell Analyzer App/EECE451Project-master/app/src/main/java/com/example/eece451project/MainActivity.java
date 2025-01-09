package com.example.eece451project;

import android.Manifest;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.sqlite.SQLiteDatabase;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.Bundle;
import android.telephony.CellIdentityGsm;
import android.telephony.CellIdentityLte;
import android.telephony.CellIdentityWcdma;
import android.telephony.CellInfo;
import android.telephony.CellInfoGsm;
import android.telephony.CellInfoLte;
import android.telephony.CellInfoWcdma;
import android.telephony.CellSignalStrengthGsm;
import android.telephony.CellSignalStrengthLte;
import android.telephony.CellSignalStrengthWcdma;
import android.telephony.TelephonyManager;
import android.widget.TextView;
import android.widget.Toast;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import java.io.IOException;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.concurrent.Executor;
import java.io.DataOutputStream;



public class MainActivity extends AppCompatActivity {
    TextView signalStrengthText;
    TextView snrText;
    TextView frequencyText;
    TextView timeText;
    TextView cellIdText;
    TextView networkTypeText;
    TextView networkOperatorText;
    private static final int PERMISSION_REQUEST_CODE = 1001;

    private DatabaseHelper dbHelper;
    MyThread myThread;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        signalStrengthText = findViewById(R.id.signalStrengthText);
        snrText = findViewById(R.id.snrText);
        frequencyText = findViewById(R.id.frequencyText);
        timeText = findViewById(R.id.timeText);
        cellIdText = findViewById(R.id.cellIdText);
        networkTypeText = findViewById(R.id.networkTypeText);
        networkOperatorText = findViewById(R.id.networkOperatorText);
        networkOperatorText.setText(getOperator());

        dbHelper = new DatabaseHelper(this);

        queryCellInfo();
        myThread = new MyThread();
        new Thread(myThread).start();
    }

    private boolean checkPermission() {
        return ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) ==
                PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) ==
                        PackageManager.PERMISSION_GRANTED;
    }

    private void requestPermission() {
        ActivityCompat.requestPermissions(this,
                new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.READ_PHONE_STATE},
                PERMISSION_REQUEST_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                queryCellInfo();
            } else {
                Toast.makeText(this, "Permission denied", Toast.LENGTH_SHORT).show();
            }
        }
    }

    public boolean checkMobileNet(Context context) {//Checks if device is connected to a mobile network
        ConnectivityManager connectivityManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        if (connectivityManager != null) {
            Network network = connectivityManager.getActiveNetwork();
            NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
            return capabilities != null && capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR);
        }
        return false;
    }

    public static boolean checkWifi(Context context) {//Checks if the device is connected to a WiFi network
        ConnectivityManager connectivityManager = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
        if (connectivityManager != null) {
                Network network = connectivityManager.getActiveNetwork();
                NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
                return capabilities != null && capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI);
        }
        return false;
    }

    public String getOperator() {
        TelephonyManager manager = (TelephonyManager) getSystemService(TelephonyManager.class);
        return Objects.requireNonNull(manager.getNetworkOperatorName());
    }

    public String getNetworkType(int networkType) {
        switch (networkType) {
            case TelephonyManager.NETWORK_TYPE_GSM:
                return "GSM";
            case TelephonyManager.NETWORK_TYPE_GPRS:
                return "GPRS";
            case TelephonyManager.NETWORK_TYPE_EDGE:
                return "EDGE";
            case TelephonyManager.NETWORK_TYPE_UMTS:
                return "UMTS";
            case TelephonyManager.NETWORK_TYPE_HSDPA:
                return "HSDPA";
            case TelephonyManager.NETWORK_TYPE_LTE:
                return "LTE";
            case TelephonyManager.NETWORK_TYPE_NR:
                return "New Radio (5G)";
            default:
                return "Outside Scope";
        }
    }

    private void queryCellInfo() {
        // Check if permissions are granted
        if (checkPermission()) {
            // Permissions are granted, proceed with querying cell info
            TelephonyManager telephonyManager = (TelephonyManager) getSystemService(TELEPHONY_SERVICE);
            int networkType = telephonyManager.getNetworkType();
            networkTypeText.setText(getNetworkType(networkType));
            Executor executor = new Executor() {
                @Override
                public void execute(Runnable command) {
                }
            };
            TelephonyManager.CellInfoCallback callback = null;
            callback = new TelephonyManager.CellInfoCallback() {
                @Override
                public void onCellInfo(@NonNull List<CellInfo> cellInfo) {
                }
            };
            telephonyManager.requestCellInfoUpdate(executor, callback);
            List<CellInfo> cellInfoList = telephonyManager.getAllCellInfo();
            //Log.d("List of Values", String.valueOf(cellInfoList));
            if (cellInfoList != null) {
                String date = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                timeText.setText(date);
                for (CellInfo cellInfo : cellInfoList) {
                    if (cellInfo instanceof CellInfoGsm) {
                        CellInfoGsm cellInfoGsm = (CellInfoGsm) cellInfo;
                        CellSignalStrengthGsm cellSignalStrengthGsm = cellInfoGsm.getCellSignalStrength();
                        int signalStrength = cellSignalStrengthGsm.getDbm();
                        signalStrengthText.setText(signalStrength + "dBm");

                        CellIdentityGsm cellIdentityGsm = cellInfoGsm.getCellIdentity();
                        int CellId = cellIdentityGsm.getCid();
                        cellIdText.setText(String.valueOf(CellId));

                        //not applicable for GSM
                        snrText.setText(String.valueOf("NONE"));
                        frequencyText.setText(String.valueOf("NONE"));
                        insertCellInfo(networkOperatorText.getText().toString(), signalStrengthText.getText().toString(), snrText.getText().toString(),networkTypeText.getText().toString(), frequencyText.getText().toString(), cellIdText.getText().toString(), timeText.getText().toString());

                    } else if (cellInfo instanceof CellInfoWcdma) { //WCDMA = UMTS
                        CellInfoWcdma cellInfoUmts = (CellInfoWcdma) cellInfo;
                        CellSignalStrengthWcdma cellSignalStrengthUmts = cellInfoUmts.getCellSignalStrength();
                        int signalStrength = cellSignalStrengthUmts.getDbm();
                        signalStrengthText.setText(signalStrength + "dBm");

                        CellIdentityWcdma cellIdentityUmts = cellInfoUmts.getCellIdentity();
                        int CellId = cellIdentityUmts.getCid();
                        cellIdText.setText(String.valueOf(CellId));

                        //UARFCN stands for UTRA Absolute Radio Frequency Channel Number
                        //Frequency Band = UARFCNx0.2
                        int UARFCN = cellIdentityUmts.getUarfcn();
                        float frequencyBand = (float) (UARFCN * 0.2);
                        frequencyText.setText(String.valueOf(frequencyBand));

                        //not available
                        snrText.setText(String.valueOf("None"));

                        insertCellInfo(networkOperatorText.getText().toString(), signalStrengthText.getText().toString(), snrText.getText().toString(),networkTypeText.getText().toString(), frequencyText.getText().toString(), cellIdText.getText().toString(), timeText.getText().toString());

                    } else if(cellInfo instanceof CellInfoLte){
                        CellInfoLte cellInfoLte = (CellInfoLte) cellInfo;

                        CellSignalStrengthLte cellSignalStrengthLte = cellInfoLte.getCellSignalStrength();
                        int signalStrength = cellSignalStrengthLte.getDbm();
                        signalStrengthText.setText(signalStrength + "dBm");

                        CellIdentityLte cellIdentityLte = cellInfoLte.getCellIdentity();
                        int CellId = cellIdentityLte.getCi();
                        cellIdText.setText(String.valueOf(CellId));

                        int SNR = cellSignalStrengthLte.getRssnr();
                        snrText.setText(String.valueOf(SNR));

                        int frequencyBand =  cellIdentityLte.getBandwidth();
                        frequencyText.setText(String.valueOf(frequencyBand));

                        insertCellInfo(networkOperatorText.getText().toString(), signalStrengthText.getText().toString(), snrText.getText().toString(),networkTypeText.getText().toString(), frequencyText.getText().toString(), cellIdText.getText().toString(), timeText.getText().toString());
                    }
                }
            }
        } else {
            // Permissions are not granted, request them
            requestPermission();
        }
    }

    private void insertCellInfo(String operator, String signalPower, String snr, String networkType, String frequencyBand, String cellId, String timestamp) {
        SQLiteDatabase db = dbHelper.getWritableDatabase();
        db.beginTransaction();

        try{
            ContentValues values = new ContentValues();
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_OPERATOR, operator);
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_SIGNAL_POWER, signalPower);
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_SNR, snr);
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_NETWORK_TYPE, networkType);
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_FREQUENCY_BAND, frequencyBand);
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_CELL_ID, cellId);
            values.put(CellInfoContract.CellInfoEntry.COLUMN_NAME_TIMESTAMP, timestamp);

            long newRowId = db.insert(CellInfoContract.CellInfoEntry.TABLE_NAME, null, values);
            if (newRowId == -1) {
                Toast.makeText(this, "Error inserting cell info", Toast.LENGTH_SHORT).show();
                Log.e("Insertion Error", "Error inserting cell info");
            } else {
                Toast.makeText(this, "Cell info inserted with row ID: " + newRowId, Toast.LENGTH_SHORT).show();
            }
            db.setTransactionSuccessful();
        }
        catch (Exception e) {
            e.printStackTrace();
            Log.e("Insertion Error", "Error inserting cell info: " + e.getMessage());
        } finally {
            db.endTransaction();
        }
    }

    @Override
    protected void onDestroy() {
        dbHelper.close();
        super.onDestroy();
    }

    private class MyThread implements Runnable{
        private volatile String msg="";
        Socket socket;
        DataOutputStream dos;
        @Override
        public void run() {

            try {
                String data= retrieveDataFromDatabase();
                socket = new Socket("ip address", 5678);
                dos=new DataOutputStream(socket.getOutputStream());
                dos.writeUTF(msg);
                dos.close();
                dos.flush();
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }

        }
        private String retrieveDataFromDatabase() {
            StringBuilder dataBuilder = new StringBuilder();
            // Retrieve data from SQLite database here
            // You can use dbHelper to access the SQLite database and retrieve the data
            // Example:
            // SQLiteDatabase db = dbHelper.getReadableDatabase();
            // Cursor cursor = db.rawQuery("SELECT * FROM " + CellInfoContract.CellInfoEntry.TABLE_NAME, null);
            // Loop through the cursor and append data to dataBuilder

            // Dummy data for demonstration purposes
            dataBuilder.append("operator1,signalPower1,snr1,networkType1,frequencyBand1,cellId1,");
            dataBuilder.append("operator2,signalPower2,snr2,networkType2,frequencyBand2,cellId2,");

            return dataBuilder.toString();
        }

        public void sendMsg() {
            new Thread(this).start();
        }
    }
}
