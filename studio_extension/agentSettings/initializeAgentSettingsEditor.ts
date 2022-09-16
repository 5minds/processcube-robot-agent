import { Studio } from '@atlas-engine/atlas_studio_sdk';
import * as fs from 'fs';

import { RobotAgentsConfigEditor } from './RobotAgentsConfigEditor';
import { RobotAgentsConfigDocument } from './RobotAgentsConfigDocument';
import { ROBOT_AGENT_CONFIG_FILE } from './getRobotAgents';

export function initializeAgentSettingsEditor(studio: Studio): void {
  studio.menus.registerMenuModifier('std/activity-bar/settings', menu => {
    return studio.menus.appendToMenu(menu, [{
        type: 'divider',
      },{
        label: 'Robot Agents',
        command: 'plugin.robot-agents.editAgents',
        type: 'command',
        id: 'std/activity-bar/settings/robot-agents',
      }]);
  });

  studio.commands.registerInCommandSearch('plugin.robot-agents.editAgents', 'Robot Agents: Edit Agents', () => {
    studio.editors.focusOrOpenEditorDocument(studio.solution.getSolution()?.baseUri + ROBOT_AGENT_CONFIG_FILE)
  }, () => studio.solution.getSolution() !== null && fs.existsSync(studio.files.getLocalFilenameForUri(studio.solution.getSolution()?.baseUri + ROBOT_AGENT_CONFIG_FILE)));

  studio.editors.registerDocumentType('editor-document-robot-agents', {
    uriMatch: /\.processcube\/robot-agent\/agents\.json$/,
    rendererKey: 'RobotAgentsConfigEditor',
    rendererConstructor: RobotAgentsConfigEditor,
    modelKey: 'RobotAgentsConfigDocument',
    modelConstructor: RobotAgentsConfigDocument,
    icon: 'far fa-cog'
  });
}
