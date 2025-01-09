package com.example.eece451project;
import java.io.DataInputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;

public class MyServer {
    private static final int PORT = 5678;

    // Map to store statistics
    private static Map<String, Integer> operatorCounts = new HashMap<>();
    private static Map<String, Integer> networkTypeCounts = new HashMap<>();
    private static Map<String, Integer> signalPowerNetworkTypeSum = new HashMap<>();
    private static Map<String, Integer> signalPowerDeviceSum = new HashMap<>();
    private static Map<String, Integer> snrNetworkTypeSum = new HashMap<>();

    public static void main(String[] args) {
        System.out.println("The server is running at port number " + PORT);

        try (ServerSocket ss = new ServerSocket(PORT)) {
            while (true) {
                Socket socket = ss.accept();
                handleClient(socket);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void handleClient(Socket socket) {
        try (DataInputStream dis = new DataInputStream(socket.getInputStream())) {
            String msg = dis.readUTF();
            processMessage(msg);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void processMessage(String msg) {
        // Split the received message into database entries
        String[] entries = msg.split(",");

        // Process each database entry
        for (String entry : entries) {
            // Parse the entry and extract relevant data
            String[] fields = entry.split(";"); // Example format: "operator;signalPower;snr;networkType;frequencyBand;cellId;timestamp"
            String operator = fields[0];
            String networkType = fields[3];
            int signalPower = Integer.parseInt(fields[1]);
            int snr = Integer.parseInt(fields[2]);

            // Update statistics
            updateStatistics(operator, networkType, signalPower, snr);
        }

        // Calculate and print percentages
        // You can implement the logic for calculating percentages here
    }

    private static void updateStatistics(String operator, String networkType, int signalPower, int snr) {
        // Update operator counts
        operatorCounts.put(operator, operatorCounts.getOrDefault(operator, 0) + 1);

        // Update network type counts
        networkTypeCounts.put(networkType, networkTypeCounts.getOrDefault(networkType, 0) + 1);

        // Update signal power sums per network type
        signalPowerNetworkTypeSum.put(networkType, signalPowerNetworkTypeSum.getOrDefault(networkType, 0) + signalPower);

        // Update signal power sum per device
        signalPowerDeviceSum.put(operator, signalPowerDeviceSum.getOrDefault(operator, 0) + signalPower);

        // Update SNR sums per network type
        snrNetworkTypeSum.put(networkType, snrNetworkTypeSum.getOrDefault(networkType, 0) + snr);
    }

    // Implement methods to calculate percentages here
}

