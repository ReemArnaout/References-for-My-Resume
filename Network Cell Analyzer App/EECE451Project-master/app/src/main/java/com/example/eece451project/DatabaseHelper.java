package com.example.eece451project;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DatabaseHelper extends SQLiteOpenHelper {
    public static final int DATABASE_VERSION = 1;
    public static final String DATABASE_NAME = "CellInfo.db";

    private static final String SQL_CREATE_ENTRIES =
            "CREATE TABLE " + CellInfoContract.CellInfoEntry.TABLE_NAME + " (" +
                    CellInfoContract.CellInfoEntry._ID + " INTEGER PRIMARY KEY," + //_ID represents ID of network analysis entry, inherited from BaseColumns
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_OPERATOR + " TEXT," +
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_SIGNAL_POWER + " TEXT," +
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_SNR + " TEXT," +
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_NETWORK_TYPE + " TEXT," +
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_FREQUENCY_BAND + " TEXT," +
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_CELL_ID + " TEXT," +
                    CellInfoContract.CellInfoEntry.COLUMN_NAME_TIMESTAMP + " TEXT)";

    private static final String SQL_DELETE_ENTRIES =
            "DROP TABLE IF EXISTS " + CellInfoContract.CellInfoEntry.TABLE_NAME;

    //Context instance represents current state of app and provide access to application-specific resources and classes (interaction with Android system)
    public DatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    //Method called when database created for first time
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(SQL_CREATE_ENTRIES);
    }

    //Called when database version number is incremented --> need to upgrade database
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL(SQL_DELETE_ENTRIES);
        onCreate(db); //re-create database with updated schema
    }

    public void onDowngrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + CellInfoContract.CellInfoEntry.TABLE_NAME);
        onCreate(db);
    }
}

