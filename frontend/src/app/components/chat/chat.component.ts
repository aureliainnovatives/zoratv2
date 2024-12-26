import { Component, OnInit, OnDestroy } from '@angular/core';
import { ChatService, ChatResponse } from '../../services/chat.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html'
})
export class ChatComponent implements OnInit, OnDestroy {
  messages: any[] = [];
  currentMessage = '';
  private chatSubscription?: Subscription;
  currentStreamedResponse = '';

  constructor(private chatService: ChatService) {}

  ngOnInit() {}

  ngOnDestroy() {
    if (this.chatSubscription) {
      this.chatSubscription.unsubscribe();
    }
  }

  sendMessage() {
    if (!this.currentMessage.trim()) return;

    // Add user message to chat
    this.messages.push({
      role: 'user',
      content: this.currentMessage
    });

    // Reset current streamed response
    this.currentStreamedResponse = '';
    
    // Add placeholder for assistant response
    const assistantMessageIndex = this.messages.length;
    this.messages.push({
      role: 'assistant',
      content: '',
      streaming: true
    });

    // Subscribe to streaming response
    this.chatSubscription = this.chatService
      .sendMessage(this.currentMessage, 'GPT-3.5 Turbo')
      .subscribe({
        next: (response: ChatResponse) => {
          if (response.type === 'chunk' && response.data) {
            // Append chunk to current streamed response
            this.currentStreamedResponse += response.data.content;
            // Update the assistant's message
            this.messages[assistantMessageIndex].content = this.currentStreamedResponse;
          } else if (response.type === 'complete') {
            // Mark streaming as complete
            this.messages[assistantMessageIndex].streaming = false;
          }
        },
        error: (error) => {
          console.error('Chat error:', error);
          // Update the assistant's message to show error
          this.messages[assistantMessageIndex].content = 'Error: ' + (error.message || 'Failed to process message');
          this.messages[assistantMessageIndex].error = true;
          this.messages[assistantMessageIndex].streaming = false;
        }
      });

    // Clear input
    this.currentMessage = '';
  }
} 