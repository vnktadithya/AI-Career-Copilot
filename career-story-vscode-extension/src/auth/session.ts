import * as vscode from "vscode";
import { AUTH_STORAGE_KEY } from "../config";

let secretStorage: vscode.SecretStorage;

export function initAuth(context: vscode.ExtensionContext) {
  secretStorage = context.secrets;
}

export async function getAuthToken(): Promise<string | null> {
  const token = await secretStorage.get(AUTH_STORAGE_KEY);
  return token ?? null;
}

export async function setAuthToken(token: string) {
  await secretStorage.store(AUTH_STORAGE_KEY, token);
}

export async function clearAuthToken() {
  await secretStorage.delete(AUTH_STORAGE_KEY);
}
