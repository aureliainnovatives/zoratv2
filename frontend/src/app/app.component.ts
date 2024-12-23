import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatSnackBarModule],
  templateUrl: './app.component.html'
})
export class AppComponent {
  title = 'Zorat AI';
}
