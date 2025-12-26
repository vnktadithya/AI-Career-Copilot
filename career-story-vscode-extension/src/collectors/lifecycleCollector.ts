import * as vscode from "vscode";
import { buildAndSendEvent } from "../events/eventBuilder";

export function initLifecycleCollector(
  context: vscode.ExtensionContext
) {
  // Repo opened signal
  if (vscode.workspace.workspaceFolders?.length) {
    buildAndSendEvent("repo_opened", {
      workspace:
        vscode.workspace.workspaceFolders[0].uri.fsPath,
    });
  }
}
