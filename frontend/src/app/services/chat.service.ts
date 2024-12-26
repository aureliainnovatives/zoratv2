import { Injectable, signal, computed } from '@angular/core';
import { Socket } from 'socket.io-client';
import { environment } from '../../environments/environment';
import { io } from 'socket.io-client';
import { EventEmitter } from '@angular/core';

export interface ChatMessage {
  content: string;
  type: 'sent' | 'received';
  timestamp: Date;
  complete?: boolean;
  id?: string; // Add unique ID for message tracking
}

export interface ChatState {
  messages: ChatMessage[];
  isConnected: boolean;
  isTyping: boolean;
  sessionId: string;
  currentDate: Date;
  isStreamingMode: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private socket!: Socket;
  private messageIdCounter = 0;
  private CHAR_DELAY = 20; // milliseconds between characters
  
  // State management using signals
  private state = signal<ChatState>({
    messages: [{
      content: "Hello! I am your AI assistant. How can I help you today?",
      type: 'received',
      timestamp: new Date(),
      complete: true
    }],
    isConnected: false,
    isTyping: false,
    sessionId: Math.random().toString(36).substring(7).toUpperCase(),
    currentDate: new Date(),
    isStreamingMode: false // We'll simulate streaming on frontend
  });

  // Computed values and selectors
  public messages = computed(() => this.state().messages);
  public isConnected = computed(() => this.state().isConnected);
  public isTyping = computed(() => this.state().isTyping);
  public sessionId = computed(() => this.state().sessionId);
  public currentDate = computed(() => this.state().currentDate);
  public isStreamingMode = computed(() => this.state().isStreamingMode);

  // Event emitters for component communication
  public onConnect = new EventEmitter<void>();
  public onDisconnect = new EventEmitter<void>();
  public onError = new EventEmitter<string>();
  public onMessageReceived = new EventEmitter<ChatMessage>();

  constructor() {
    console.log('[Socket] Initializing chat service');
    console.log('[Socket] Streaming mode:', environment.chat.useStreaming ? 'enabled' : 'disabled');
    this.initializeSocket();
  }

  private initializeSocket(): void {
    console.log('[Socket] Socket URL:', environment.socketUrl);
    console.log('[Socket] Socket Namespace:', environment.chat.socketNamespace);

    this.socket = io(`${environment.socketUrl}${environment.chat.socketNamespace}`, {
      path: '/socket.io',
      autoConnect: false,
      reconnectionAttempts: environment.chat.reconnectAttempts,
      reconnectionDelay: environment.chat.reconnectInterval,
      auth: {
        token: localStorage.getItem('auth_token')
      },
      transports: ['websocket', 'polling']
    });

    this.setupSocketListeners();
  }

  private setupSocketListeners(): void {
    this.socket.onAny((event: string, ...args: any[]) => {
      console.log(`[Socket Debug] Event: ${event}, Socket ID: ${this.socket.id}`, args);
    });

    this.socket.on('connect', () => {
      console.log('[Socket] Connected, ID:', this.socket.id);
      this.updateState({ isConnected: true });
      this.onConnect.emit();
    });

    this.socket.on('disconnect', () => {
      console.log('[Socket] Disconnected');
      this.updateState({ isConnected: false });
      this.onDisconnect.emit();
      this.addSystemMessage("Connection lost. Attempting to reconnect...");
    });

    this.socket.on('chat-response', this.handleChatResponse.bind(this));

    this.socket.on('error', (error: any) => {
      console.error('[Socket] Error:', error);
      this.onError.emit(error.message || 'Socket error occurred');
    });
  }

  private async handleChatResponse(response: any) {
    console.log('[Socket] Received response:', response);
    
    // Extract content based on response format
    let content = '';
    if (response.type === 'message' && response.data) {
      if (typeof response.data === 'string') {
        content = response.data.trim();
      } else if (typeof response.data === 'object') {
        // Handle different response formats
        if (response.data.assistant) {
          content = response.data.assistant.trim();
        } else if (response.data.content) {
          content = response.data.content.trim();
        } else if (response.data.message) {
          content = response.data.message.trim();
        } else if (response.data.response) {
          content = response.data.response.trim();
        }
      }
    }

    if (!content) {
      console.log('[Socket] No content in response:', response.data);
      return;
    }

    console.log('[Socket] Processing content:', content.substring(0, 100) + '...');
    
    // Create an empty response message with unique ID
    const messageId = `msg_${++this.messageIdCounter}`;
    const emptyResponse: ChatMessage = {
      content: '',
      type: 'received',
      timestamp: new Date(),
      complete: false,
      id: messageId
    };

    // Add empty message to state
    this.updateState({
      messages: [...this.state().messages, emptyResponse]
    });

    // Simulate typing effect
    await this.simulateTyping(content, messageId);
  }

  private async simulateTyping(content: string, messageId: string) {
    let currentContent = '';
    // Split into paragraphs first
    const paragraphs = content.split('\n\n');
    const PARAGRAPH_DELAY = 400;
    const WORD_DELAY = 50;
    
    for (let i = 0; i < paragraphs.length; i++) {
      const paragraph = paragraphs[i].trim();
      if (!paragraph) continue;

      // Add newline between paragraphs except for the first one
      if (currentContent) {
        currentContent += '\n\n';
        this.updateMessageContent(messageId, currentContent);
        await new Promise(resolve => setTimeout(resolve, PARAGRAPH_DELAY));
      }

      // Split into words while preserving spaces and punctuation
      const words = paragraph.split(/(?<=\s)|(?=\s)/g).filter(Boolean);
      
      for (const word of words) {
        currentContent += word;
        this.updateMessageContent(messageId, currentContent);
        
        // Only delay for actual words, not spaces
        if (!/^\s+$/.test(word)) {
          await new Promise(resolve => setTimeout(resolve, WORD_DELAY));
        }
      }
    }

    // Mark message as complete
    this.updateMessageComplete(messageId);
    this.updateState({ isTyping: false });
  }

  private updateMessageContent(messageId: string, content: string): void {
    // Use requestAnimationFrame to batch updates
    requestAnimationFrame(() => {
      this.state.update(state => {
        const messages = state.messages.map(msg =>
          msg.id === messageId ? { ...msg, content } : msg
        );
        return { ...state, messages };
      });
    });
  }

  private updateMessageComplete(messageId: string): void {
    this.state.update(state => ({
      ...state,
      messages: state.messages.map(msg => 
        msg.id === messageId ? { ...msg, complete: true } : msg
      )
    }));
  }

  private updateState(partialState: Partial<ChatState>): void {
    this.state.update(state => ({
      ...state,
      ...partialState
    }));
  }

  private addSystemMessage(content: string): void {
    const systemMessage: ChatMessage = {
      content,
      type: 'received',
      timestamp: new Date(),
      complete: true,
      id: `system_${++this.messageIdCounter}`
    };
    this.updateState({
      messages: [...this.state().messages, systemMessage]
    });
  }

  public connect(): void {
    if (!this.socket.connected) {
      console.log('[Socket] Connecting...');
      this.socket.connect();
    }
  }

  public disconnect(): void {
    if (this.socket.connected) {
      console.log('[Socket] Disconnecting...');
      this.socket.disconnect();
    }
  }

  public sendMessage(content: string): void {
    if (!content.trim() || !this.isConnected()) {
      console.log('[Socket] Message not sent:', { content, connected: this.isConnected() });
      return;
    }

    const userMessage: ChatMessage = {
      content: content.trim(),
      type: 'sent',
      timestamp: new Date(),
      id: `user_${++this.messageIdCounter}`
    };

    // Add user message
    this.updateState({
      messages: [...this.state().messages, userMessage],
      isTyping: true
    });

    const messageData = {
      content,
      llm_name: environment.chat.defaultLLM,
      useStreaming: false, // Always use normal chat
      endpoint: environment.chat.plainEndpoint,
      metadata: {
        timestamp: new Date().toISOString(),
        client: 'web',
        version: '1.0.0'
      }
    };

    console.log('[Socket] Sending message using normal chat');
    console.log('[Socket] Using endpoint:', messageData.endpoint);
    this.socket.emit('message', messageData);
  }
} 