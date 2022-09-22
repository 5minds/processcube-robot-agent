import { Studio } from '@atlas-engine/atlas_studio_sdk';
import * as fs from 'fs';

import { RobotAgentsConfigEditor } from './RobotAgentsConfigEditor';
import { RobotAgentsConfigDocument } from './RobotAgentsConfigDocument';
import { AGENT_CONFIG_FILE_NAME, SOLUTION_ROBOT_DIRECTORY } from './getRobotAgents';

export function initializeAgentSettingsEditor(studio: Studio): void {
  studio.menus.registerMenuModifier('std/activity-bar/settings', menu =>
    studio.menus.appendToMenu(menu, [{
        type: 'divider',
      }, {
        label: 'Robot Agents',
        command: 'plugin.robot-agents.editAgents',
        type: 'command',
        id: 'std/activity-bar/settings/robot-agents',
      }]
    )
  );

  studio.commands.registerInCommandSearch(
    'plugin.robot-agents.editAgents',
    'Robot Agents: Edit Agents',
    () => studio.editors.focusOrOpenEditorDocument(studio.solution.getSolution()?.baseUri + SOLUTION_ROBOT_DIRECTORY +  AGENT_CONFIG_FILE_NAME),
    () => studio.solution.hasOpenSolution()
      && fs.existsSync(studio.files.getLocalFilenameForUri(studio.solution.getSolution()?.baseUri + SOLUTION_ROBOT_DIRECTORY + AGENT_CONFIG_FILE_NAME))
  );

  studio.editors.registerDocumentType('editor-document-robot-agents', {
    uriMatch: /\.processcube\/robot-agent\/agents\.json$/,
    rendererKey: 'RobotAgentsConfigEditor',
    rendererConstructor: RobotAgentsConfigEditor,
    modelKey: 'RobotAgentsConfigDocument',
    modelConstructor: RobotAgentsConfigDocument,
    icon: 'far fa-robot'
  });

  studio.icons.registerIcons({})
}
