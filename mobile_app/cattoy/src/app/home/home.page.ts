import { Component } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { AlertController } from '@ionic/angular';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  myWebSocket: WebSocketSubject<any> = webSocket('ws://localhost:3000');
  directionValue: any = 50;
  moveValue: any = 50;
  maxSpeed = 70;
  connectionState: boolean = false;
  autopilotOn = false;
  private file: File | null = null;

  constructor(public alertController: AlertController) {
    /*this.myWebSocket.
    subscribe(    
      msg => console.log('message received: ' + msg), 
      // Called whenever there is a message from the server    
      err => console.log(err), 
      // Called if WebSocket API signals some kind of error    
      () => console.log('complete') 
      // Called when connection is closed (for whatever reason)  
   );*/
  }

  startAutopilot() {
    if(this.autopilotOn === false) {
      console.log("Enabling Autopilot");
      this.myWebSocket.next({ "motor1PW": 0, "motor1D": 0, "motor2PW": 0, "motor2D": 0, "autopilot": true });
      return;
    }
    if(this.autopilotOn === true) {
      console.log("Disabling Autopilot");
      this.myWebSocket.next({ "motor1PW": 0, "motor1D": 0, "motor2PW": 0, "motor2D": 0, "autopilot": false });
      return;
    }
  }

  connectToServer() {
    if(this.connectionState === true) {
      console.log("Connection already established");
      return;
    }

    this.myWebSocket.asObservable().subscribe({
      next: data => {console.log(data); this.connectionState = true},
      error: error => { console.log(error); this.connectionState = false; this.presentAlert("Could not connect!", "Connection Error")},
      complete: () => { console.log("Connection Completed"); this.connectionState = false }
    });
  }

  updateSlider() {
    if (this.moveValue > 50 || this.moveValue < 50) {
      let powerLeft = this.moveValue > 50 ? this.moveValue - 50 : 50 - this.moveValue;
      let powerRight = this.moveValue > 50 ? this.moveValue - 50 : 50 - this.moveValue;
      let direction = this.moveValue > 50 ? 0 : 1;

      if (this.directionValue > 50) {
        let steering = this.directionValue - 50;
        powerLeft = powerLeft + steering;
        powerRight = powerRight - steering;
        if (powerRight < 0) {
          powerRight = 0;
        }
        if (powerLeft > 70) {
          powerLeft = this.maxSpeed;
        }
        this.myWebSocket.next({ "motor1PW": powerLeft, "motor1D": direction, "motor2PW": powerRight, "motor2D": direction, "autopilot": false });
        console.log('updateSlider:', { "motor1PW": powerLeft, "motor1D": direction, "motor2PW": powerRight, "motor2D": direction, "autopilot": false });
        return;
      }

      if (this.directionValue < 50) {
        let steering = 50 - this.directionValue;
        powerLeft = powerLeft - steering;
        powerRight = powerRight + steering;
        if (powerLeft < 0) {
          powerLeft = 0;
        }
        if (powerRight > 70) {
          powerRight = this.maxSpeed;
        }
        this.myWebSocket.next({ "motor1PW": powerLeft, "motor1D": direction, "motor2PW": powerRight, "motor2D": direction, "autopilot": false });
        console.log('updateSlider:', { "motor1PW": powerLeft, "motor1D": direction, "motor2PW": powerRight, "motor2D": direction, "autopilot": false });
        return;
      }
      this.myWebSocket.next({ "motor1PW": powerLeft, "motor1D": direction, "motor2PW": powerRight, "motor2D": direction, "autopilot": false });
      console.log('updateSlider:', { "motor1PW": powerLeft, "motor1D": direction, "motor2PW": powerRight, "motor2D": direction, "autopilot": false });
      return;

    }

    if (this.directionValue > 50 || this.directionValue < 50) {
      if (this.directionValue > 50) {
        let power = this.directionValue - 50;
        this.myWebSocket.next({ "motor1PW": power, "motor1D": 0, "motor2PW": power, "motor2D": 1, "autopilot": false });
        console.log('updateSlider:', { "motor1PW": power, "motor1D": 0, "motor2PW": power, "motor2D": 1, "autopilot": false })
        return;
      }
      if (this.directionValue < 50) {
        let power = 50 - this.directionValue;
        this.myWebSocket.next({ "motor1PW": power, "motor1D": 1, "motor2PW": power, "motor2D": 0, "autopilot": false });
        console.log('updateSlider:', { "motor1PW": power, "motor1D": 1, "motor2PW": power, "motor2D": 0, "autopilot": false })
        return;
      }
    }
  }

  releaseMoveSlider() {
    console.log('releaseMoveSlider');
    this.moveValue = 50;
  }

  releaseDirectionSlider() {
    console.log('releaseDirectionSlider');
    this.directionValue = 50;
  }

  sendStaticAudio(file: string){
  if(/(\.mp3)$/i.test(file)){
    this.myWebSocket.next({ "play_audio": file });
  }else {
    this.presentAlert("Nah nah nah, don't edit the app!")
  }
  }

  handleFileInput(event: Event) {
    const element = event.target as HTMLInputElement;
    const files = element.files;
    if (files && files.length > 0) {
      const file = files[0];
      if(/(\.mp3|\.ogg|\.wav)$/i.test(file.name)) {
        if(file.size > 10000000) {
          this.file = null;
          this.presentAlert("File too large, please select a file smaller than 10MB");
        }else{
          this.file = file;
        }
      }else{
        this.file = null;
        this.presentAlert("Wrong file format, please select an audio file");
      }
    } else {
      console.error("No file selected!");
      this.file = null;
      this.presentAlert("Please select an audio file");
    }
  }

  sendFile() {
    if (this.file) {
      const reader = new FileReader();
      reader.readAsDataURL(this.file);
      reader.onload = () => {
        console.log("Sending file: ", reader.result);
        const base64 = reader.result as string;
        this.myWebSocket.next({ "operation": "file_transfer", "file": base64});
      };
    } else {
      console.error("No file selected!");
      this.presentAlert("Please select an audio file");
    }
  }

  async presentAlert(message: string, header: string = "File Upload Error") {
    const alert = await this.alertController.create({
      header: header,
      message: message,
      buttons: ['OK']
    });
  
    await alert.present();
  }
}
