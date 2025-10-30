import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import { ChatMessage } from "../types";
import { ChatService } from "../services/chatService";
import Message from "./Message";
import MessageInput from "./MessageInput";

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background-color: #f8f9fa;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  padding: 16px 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
`;

const Subtitle = styled.p`
  margin: 4px 0 0 0;
  font-size: 0.9rem;
  opacity: 0.9;
`;

const StatusIndicator = styled.div<{ connected: boolean }>`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  margin-top: 8px;

  &::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: ${(props) => (props.connected ? "#28a745" : "#dc3545")};
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
`;

const SuggestedQuestions = styled.div`
  margin-top: 20px;
`;

const QuestionButton = styled.button`
  display: block;
  width: 100%;
  margin: 8px 0;
  padding: 12px 16px;
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  color: #495057;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;

  &:hover {
    background-color: #f8f9fa;
    border-color: #007bff;
    transform: translateY(-1px);
  }
`;

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "Quel est le numéro de compte du crédit logement?",
    "Combien de jours a pris le traitement du dossier CNOPS 906377038?",
    "Quel était le montant remboursé par l'AMO dans le décompte Sanlam?",
    "Quelle est la date de naissance de l'élève dans le certificat?",
    "ما هو رقم الحساب المرتبط بقرض السكن؟",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkConnection = async () => {
    try {
      const health = await ChatService.checkHealth();
      setIsConnected(health);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const generateMessageId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const handleSendMessage = async (question: string) => {
    if (!question.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateMessageId(),
      question,
      timestamp: new Date(),
    };

    const botMessage: ChatMessage = {
      id: generateMessageId(),
      question,
      timestamp: new Date(),
      isLoading: true,
      answer: "",
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
    setIsLoading(true);

    try {
      const response = await ChatService.sendMessage(question);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === botMessage.id
            ? {
                ...msg,
                answer: response.answer,
                sources: response.sources,
                processingTime: response.processing_time,
                isLoading: false,
              }
            : msg
        )
      );
    } catch (error) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === botMessage.id
            ? {
                ...msg,
                error:
                  error instanceof Error
                    ? error.message
                    : "Une erreur est survenue",
                isLoading: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    if (!isLoading) {
      handleSendMessage(question);
    }
  };

  return (
    <ChatContainer>
      <Header>
        <Title>🤖 Assistant RAG</Title>
        <Subtitle>Questions-réponses sur les documents administratifs</Subtitle>
        <StatusIndicator connected={isConnected}>
          {isConnected ? "🟢 Connecté" : "🔴 Déconnecté"}
        </StatusIndicator>
      </Header>

      <MessagesContainer>
        {messages.length === 0 ? (
          <WelcomeMessage>
            <h3>👋 Bienvenue!</h3>
            <p>
              Je peux répondre à vos questions sur les documents administratifs
              disponibles.
            </p>
            <p>Voici quelques exemples de questions:</p>

            <SuggestedQuestions>
              {suggestedQuestions.map((question, index) => (
                <QuestionButton
                  key={index}
                  onClick={() => handleSuggestedQuestion(question)}
                  disabled={isLoading || !isConnected}
                >
                  💬 {question}
                </QuestionButton>
              ))}
            </SuggestedQuestions>
          </WelcomeMessage>
        ) : (
          messages.map((message) => (
            <Message key={message.id} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading || !isConnected}
      />
    </ChatContainer>
  );
};

export default ChatBot;
