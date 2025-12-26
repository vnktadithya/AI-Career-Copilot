import * as vscode from "vscode";
import { initAuth } from "./auth/session";
import { login } from "./auth/login";
import { initLifecycleCollector } from "./collectors/lifecycleCollector";
import { initGitCollector } from "./collectors/gitCollector";
import { initWorkspaceCollector } from "./collectors/workspaceCollector";

export function activate(context: vscode.ExtensionContext) {
  console.log("[CareerStory] Extension activated");

  // Initialize auth storage
  initAuth(context);

  // 🔑 REGISTER COMMANDS
  const loginCommand = vscode.commands.registerCommand(
    "careerStory.login",
    async () => {
      await login();
    }
  );

  const logoutCommand = vscode.commands.registerCommand(
    "careerStory.logout",
    async () => {
      await vscode.window.showInformationMessage(
        "Logged out (not implemented yet)"
      );
    }
  );

  context.subscriptions.push(loginCommand, logoutCommand);

  // Initialize collectors
  initLifecycleCollector(context);
  initWorkspaceCollector(context);
  initGitCollector(context);
}

export function deactivate() {
  console.log("[CareerStory] Extension deactivated");
}


