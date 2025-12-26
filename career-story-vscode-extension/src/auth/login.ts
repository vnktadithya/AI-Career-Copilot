import * as vscode from "vscode";
import { setAuthToken } from "./session";
import { BACKEND_URL } from "../config";

const POLL_INTERVAL_MS = 2000;
const MAX_ATTEMPTS = 30; // ~60 seconds total

type VscodeLoginSessionResponse =
  | { status: "pending" }
  | { status: "expired" }
  | {
      status: "completed";
      session_token: string;
      user_id: string;
    };

type VscodeLoginInitResponse = {
  auth_url: string;
  session_id: string;
};


export async function login() {
  let session_id: string;
  let auth_url: string;

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/auth/vscode/login`, {
      method: "POST",
    });

    if (!res.ok) {
      throw new Error(`Login init failed: ${res.status}`);
    }

    const data = (await res.json()) as VscodeLoginInitResponse;
    session_id = data.session_id;
    auth_url = data.auth_url;
  } catch (err) {
    vscode.window.showErrorMessage(
      "Failed to start Career Story Copilot login."
    );
    return;
  }

  await vscode.env.openExternal(vscode.Uri.parse(auth_url));

  vscode.window.showInformationMessage(
    "Complete login in your browser to connect Career Story Copilot."
  );

  // 🔁 Poll backend for session completion
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));

    try {
      const statusRes = await fetch(
        `${BACKEND_URL}/api/v1/auth/vscode/session/${session_id}`
      );

      if (!statusRes.ok) {
        continue;
      }

      const statusData = (await statusRes.json()) as VscodeLoginSessionResponse;

      if (statusData.status === "completed") {
        await setAuthToken(statusData.session_token);

        vscode.window.showInformationMessage(
          "Career Story Copilot connected successfully."
        );
        return;
      }

      if (statusData.status === "expired") {
        vscode.window.showErrorMessage(
          "Login session expired. Please try again."
        );
        return;
      }
    } catch {
      // Network hiccup — retry silently
    }
  }

  vscode.window.showErrorMessage(
    "Login timed out. Please try again."
  );
}
