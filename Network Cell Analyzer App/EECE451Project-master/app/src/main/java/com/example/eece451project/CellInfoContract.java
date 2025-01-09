package com.example.eece451project;

import android.provider.BaseColumns;

public final class CellInfoContract {
    // Empty constructor to prevent accidental instantiation of the constructor
    private CellInfoContract() {}

    // Inner class that defines the table contents.
    public static class CellInfoEntry implements BaseColumns {
        // Table name
        public static final String TABLE_NAME = "cell_info";

        // Column names
        public static final String COLUMN_NAME_OPERATOR = "operator";
        public static final String COLUMN_NAME_SIGNAL_POWER = "signal_power";
        public static final String COLUMN_NAME_SNR = "snr";
        public static final String COLUMN_NAME_NETWORK_TYPE = "network_type";
        public static final String COLUMN_NAME_FREQUENCY_BAND = "frequency_band";
        public static final String COLUMN_NAME_CELL_ID = "cell_id";
        public static final String COLUMN_NAME_TIMESTAMP = "timestamp";
    }
}

