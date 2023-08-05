#define UART_BAUD 57600
#include <ESP8266mDNS.h>  // For ESP8266
// OR

#include "SoftwareSerial.h"

// WiFi credentials
const char* ssid = "Surya P";
const char* pwd = "9900117626";
const int port = 8;

#include <ESP8266WiFi.h>
#include <WiFiClient.h>

WiFiServer server(port);
WiFiClient client;

uint8_t buf1[1024];
uint8_t i1 = 0;
int flag = 0;

void setup() {
  delay(500);
  MDNS.begin("mynodemcu");

  Serial.begin(UART_BAUD);

  WiFi.mode(WIFI_STA);

  WiFi.begin(ssid, pwd);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(100);
  }

  //Serial.println("");
  //Serial.print("Connected to ");
  //Serial.println(ssid);
  //Serial.print("IP address: ");
  //Serial.println(WiFi.localIP());
  
  server.begin(); // start TCP server
}

void loop() {

    if (Serial.available() > 0) {
          String command = Serial.readStringUntil('\n');
          command.trim(); // Remove leading/trailing whitespaces
          //Serial.println("Arduino Data : "+command);
          if(command.equals("OBSTACLE")){
            //Serial.println(command);
            if (client && client.connected()) {
                 client.println(command);
                 //Serial.println("Sent to client = "+command);
                 command = "";
                 //Serial.println("Post Send : "+command);

            }
          }
    }
  
  if (!client || !client.connected()) {
    client = server.available();
    if (client) {
      //Serial.println("New client connected");
      //client.println("Hello from the server!"); // Send initial message to the client
    }
  }

  if (client && client.connected()) {
    if (client.available()) {
      while (client.available()) {
        buf1[i1] = (uint8_t)client.read(); // Read char from client
        if (i1 < 1023) i1++;
      }
      // Now send to UART (Arduino Uno):
      Serial.write(buf1, i1);
      //Serial.println("");

      i1 = 0;

      // Send a message to the client indicating the server received the data
      //client.println("Server received data");
    }
  }
  if(flag==0){
    delay(5000);
    Serial.println(WiFi.localIP());
    flag = 1;
  }
}
