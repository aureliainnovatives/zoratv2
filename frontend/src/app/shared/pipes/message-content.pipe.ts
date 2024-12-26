import { Pipe, PipeTransform } from '@angular/core';
import { ChatMessage } from '../../services/chat.service';

@Pipe({
  name: 'messageContent',
  standalone: true,
  pure: true
})
export class MessageContentPipe implements PipeTransform {
  transform(message: ChatMessage): string {
    return message.content?.trim() || '';
  }
} 