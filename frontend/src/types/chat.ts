export type Sender = "user" | "assistant";

export interface StartChat {
  chat_id: string;
  created_at: string;
  message: string | null;
}

export interface Chat {
  chat_id: string;
  created_at: string;
  messages: Message[];
}

export interface Message {
  message_id: string;
  sender: Sender;
  content: string;
  created_at: string;
}

export interface HTTPValidationError {
  detail?: ValidationError[];
}

interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
