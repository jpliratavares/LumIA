export interface Message {
  id: string;
  sender: 'user' | 'lumia' | 'loading' | 'error';
  text: string;
  timestamp: number; // Usaremos para ordenar e como ID único
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  // Poderíamos adicionar outras metadados do chat aqui depois
  // lastUpdated: number;
}

// Tipo para a resposta da API
export interface ApiResponse {
  answer: string;
  raw_answer?: string | null; // Opcional ou nulo
  logs?: string[]; // Opcional
  processing_time_ms?: number; // Opcional
} 