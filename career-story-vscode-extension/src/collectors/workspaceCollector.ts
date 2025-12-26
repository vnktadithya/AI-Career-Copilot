import * as vscode from "vscode";
import { buildAndSendEvent } from "../events/eventBuilder";
import crypto from "crypto";

export function initWorkspaceCollector(
  context: vscode.ExtensionContext
) {
  const disposable = vscode.workspace.onDidSaveTextDocument(
    async (doc) => {
      if (doc.isUntitled) return;
      if (doc.uri.scheme !== "file") return;

      const contentHash = crypto.createHash("sha256").update(doc.getText()).digest("hex");

      await buildAndSendEvent("working_tree_changed", {
        filePath: doc.fileName,
        language: doc.languageId,
        content_hash: contentHash
      });
    }
  );

  context.subscriptions.push(disposable);
}
