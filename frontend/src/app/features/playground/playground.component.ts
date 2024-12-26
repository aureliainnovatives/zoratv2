import { Component, signal, ViewChild, ElementRef, AfterViewChecked, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatMessage } from '../../services/chat.service';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { MessageContentPipe } from '../../shared/pipes/message-content.pipe';

@Component({
  selector: 'app-playground',
  standalone: true,
  imports: [CommonModule, FormsModule, MessageContentPipe],
  templateUrl: './playground.component.html',
  styleUrls: ['./playground.component.scss']
})
export class PlaygroundComponent implements AfterViewChecked, OnInit, OnDestroy {
  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  @ViewChild('messageTextarea') private messageTextarea!: ElementRef<HTMLTextAreaElement>;
  
  messageInput = '';
  
  // Use computed signals from chat service
  messages = this.chatService.messages;
  isTyping = this.chatService.isTyping;
  isConnected = this.chatService.isConnected;
  sessionId = this.chatService.sessionId;
  currentDate = this.chatService.currentDate;
  isStreamingMode = this.chatService.isStreamingMode;

  constructor(
    private chatService: ChatService,
    private authService: AuthService,
    private router: Router
  ) {}

  // Track messages by their ID to optimize rendering
  trackByMessageId(index: number, message: ChatMessage): string {
    return message.id || String(index);
  }

  async ngOnInit() {
    if (!this.authService.isAuthenticated()) {
      console.log('User not authenticated, redirecting to login...');
      this.router.navigate(['/login']);
      return;
    }

    this.chatService.connect();
  }

  ngOnDestroy() {
    this.chatService.disconnect();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom() {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch(err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  async sendMessage() {
    if (!this.messageInput.trim() || !this.chatService.isConnected()) {
      return;
    }

    const content = this.messageInput;
    this.messageInput = '';
    
    // Reset textarea height after sending
    if (this.messageTextarea) {
      this.messageTextarea.nativeElement.style.height = 'auto';
    }
    
    try {
      this.chatService.sendMessage(content);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }

  autoResizeTextarea(textarea: HTMLTextAreaElement): void {
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Set new height based on scrollHeight, with max-height handled by CSS
    textarea.style.height = `${Math.min(textarea.scrollHeight, 132)}px`;
  }

  handleEnterKey(event: any): void {
    const keyEvent = event as KeyboardEvent;
    if (!keyEvent.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
} 