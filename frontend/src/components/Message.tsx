import React from "react";
import styled from "styled-components";
import { ChatMessage } from "../types";

interface MessageProps {
  message: ChatMessage;
}

const MessageContainer = styled.div<{ isUser: boolean }>`
  display: flex;
  justify-content: ${(props) => (props.isUser ? "flex-end" : "flex-start")};
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 8px;
`;

const MessageWrapper = styled.div<{ isUser: boolean }>`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  max-width: 70%;
  flex-direction: ${(props) => (props.isUser ? "row-reverse" : "row")};
`;

const Avatar = styled.div<{ isUser: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  background: ${(props) =>
    props.isUser
      ? "linear-gradient(135deg, #007bff, #0056b3)"
      : "linear-gradient(135deg, #28a745, #20c997)"};
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 4px;
  line-height: 1;
  text-align: center;
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  padding: 12px 16px;
  border-radius: 18px;
  background-color: ${(props) => (props.isUser ? "#007bff" : "#f1f3f4")};
  color: ${(props) => (props.isUser ? "white" : "#333")};
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
  position: relative;

  &::before {
    content: "";
    position: absolute;
    top: 12px;
    width: 0;
    height: 0;
    border: 6px solid transparent;
    ${(props) =>
      props.isUser
        ? `
      right: -12px;
      border-left-color: #007bff;
    `
        : `
      left: -12px;
      border-right-color: #f1f3f4;
    `}
  }
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  padding: 8px 0;

  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #6c757d;
    animation: bounce 1.4s infinite ease-in-out both;

    &:nth-child(1) {
      animation-delay: -0.32s;
    }
    &:nth-child(2) {
      animation-delay: -0.16s;
    }
  }

  @keyframes bounce {
    0%,
    80%,
    100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }
`;

const MessageMeta = styled.div`
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 4px;
  text-align: right;
`;

const Sources = styled.div`
  margin-top: 8px;
  font-size: 0.8rem;
  color: #6c757d;
`;

const SourceTag = styled.span`
  background-color: #e9ecef;
  border-radius: 8px;
  padding: 2px 6px;
  margin-right: 4px;
  margin-bottom: 2px;
  display: inline-block;
  font-size: 0.7rem;
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  font-style: italic;
`;

const Message: React.FC<MessageProps> = ({ message }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getUserIcon = () => "👤";
  const getBotIcon = () => (message.isLoading ? "🤔" : "🤖");

  return (
    <MessageContainer isUser={!message.answer}>
      <MessageWrapper isUser={!message.answer}>
        <Avatar isUser={!message.answer}>
          {!message.answer ? getUserIcon() : getBotIcon()}
        </Avatar>

        <div style={{ flex: 1 }}>
          {!message.answer ? (
            // User message
            <MessageBubble isUser={true}>{message.question}</MessageBubble>
          ) : (
            // Bot message
            <MessageBubble isUser={false}>
              {message.isLoading ? (
                <LoadingDots>
                  <span></span>
                  <span></span>
                  <span></span>
                </LoadingDots>
              ) : message.error ? (
                <ErrorMessage>❌ {message.error}</ErrorMessage>
              ) : (
                <>
                  <div style={{ whiteSpace: "pre-wrap" }}>{message.answer}</div>

                  {message.sources && message.sources.length > 0 && (
                    <Sources>
                      <strong>Sources:</strong>
                      <br />
                      {message.sources.map((source, index) => (
                        <SourceTag key={index}>
                          📄 {source.replace(".txt", "")}
                        </SourceTag>
                      ))}
                    </Sources>
                  )}

                  {message.processingTime && message.processingTime > 0.01 && (
                    <MessageMeta>
                      ⚡ {message.processingTime.toFixed(2)}s •{" "}
                      {formatTime(message.timestamp)}
                    </MessageMeta>
                  )}
                </>
              )}
            </MessageBubble>
          )}

          {!message.answer && (
            <MessageMeta
              style={{
                textAlign: !message.answer ? "right" : "left",
                marginLeft: !message.answer ? "0" : "8px",
              }}
            >
              {formatTime(message.timestamp)}
            </MessageMeta>
          )}
        </div>
      </MessageWrapper>
    </MessageContainer>
  );
};

export default Message;
