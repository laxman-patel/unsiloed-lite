import { spawn } from "bun";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { writeFile } from "fs/promises";
import { Readable } from "stream";
import OpenAI from "openai";
import { Pinecone } from "@pinecone-database/pinecone";
import type { SNSMessage } from "./types/aws-types";

const s3Client = new S3Client({ region: "us-east-1" });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY! });
const index = pc.index(process.env.PINECONE_INDEX!);

Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/health") {
      return new Response("OK", { status: 200 });
    }

    if (url.pathname === "/webhook" && req.method === "POST") {
      try {
        const body = (await req.json()) as SNSMessage;

        if (body.Type === "SubscriptionConfirmation") {
          await fetch(body.SubscribeURL);
          return new Response("Subscribed", { status: 200 });
        }

        if (body.Type === "Notification") {
          const message = JSON.parse(body.Message);
          const bucket = message.Records[0].s3.bucket.name;
          const key = decodeURIComponent(message.Records[0].s3.object.key);

          const localPath = `/tmp/${key.split("/").pop()}`;
          const outputPath = `/tmp/output.json`;

          await downloadFromS3(bucket, key, localPath);

          await runPythonScript(localPath, outputPath);

          await processEmbeddings(outputPath, key);

          return new Response("Processed", { status: 200 });
        }

        return new Response("OK", { status: 200 });
      } catch (error) {
        console.error("Error:", error);
        return new Response("Error", { status: 500 });
      }
    }

    return new Response("Not Found", { status: 404 });
  },
});

async function downloadFromS3(bucket: string, key: string, localPath: string) {
  const command = new GetObjectCommand({ Bucket: bucket, Key: key });
  const response = await s3Client.send(command);

  const chunks = [];
  for await (const chunk of response.Body as Readable) {
    chunks.push(chunk);
  }

  await writeFile(localPath, Buffer.concat(chunks));
}

async function runPythonScript(inputPath: string, outputPath: string) {
  const proc = spawn(
    [
      "python3",
      "./document-processor/process-files.py",
      "--input",
      inputPath,
      "--output",
      outputPath,
    ],
    {
      stdout: "pipe",
      stderr: "pipe",
    },
  );

  await proc.exited;

  if (proc.exitCode !== 0) {
    const error = await new Response(proc.stderr).text();
    throw new Error(`Document Processor script failed: ${error}`);
  }
}

async function processEmbeddings(jsonPath: string, originalKey: string) {
  const data = await Bun.file(jsonPath).json();

  const textToEmbed = data.text || JSON.stringify(data);

  let embedding;
  try {
    const embeddingResponse = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: textToEmbed,
    });

    embedding = embeddingResponse.data[0]?.embedding;
  } catch (error) {
    console.error("Error creating embedding:", error);
    return;
  }

  try {
    await index.upsert([
      {
        id: `doc-${Date.now()}`,
        values: embedding,
        metadata: {
          ...data,
          source: originalKey,
          timestamp: new Date().toISOString(),
        },
      },
    ]);
  } catch (error) {
    console.error("Error upserting document to pinecone:", error);
  }
}

console.log("Server running on http://localhost:3000");
