package com.example.heimdall;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

public class AddTwitter extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_twitter);
    }

    public void backScreen(View view){
        Intent intent = new Intent(this, CardInfo.class);
        startActivity(intent);
    }
}
