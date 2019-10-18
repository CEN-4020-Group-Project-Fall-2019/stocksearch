package com.example.heimdall;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

public class CardInfo extends AppCompatActivity {
    private int rowCount = 1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_card_info);
        rowCount = getIntent().getIntExtra("numRows", 1);
    }

    public void backScreen(View view){
        Intent intent = new Intent(this, Home.class);
        intent.putExtra("numRows", rowCount);
        startActivity(intent);
    }

    public void addTwitter(View view){
        Intent intent = new Intent(this, AddTwitter.class);
        startActivity(intent);
    }
}
