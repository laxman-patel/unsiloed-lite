export interface SNSSubscriptionConfirmation {
  Type: "SubscriptionConfirmation";
  MessageId: string;
  Token: string;
  TopicArn: string;
  Message: string;
  SubscribeURL: string;
  Timestamp: string;
  SignatureVersion: string;
  Signature: string;
  SigningCertURL: string;
}

export interface SNSNotification {
  Type: "Notification";
  MessageId: string;
  TopicArn: string;
  Subject?: string;
  Message: string;
  Timestamp: string;
  SignatureVersion: string;
  Signature: string;
  SigningCertURL: string;
  UnsubscribeURL: string;
}

export type SNSMessage = SNSSubscriptionConfirmation | SNSNotification;
