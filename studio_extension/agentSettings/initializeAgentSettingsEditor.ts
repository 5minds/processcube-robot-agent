import { Studio } from '@atlas-engine/atlas_studio_sdk';

import { RobotAgentsConfigEditor } from './RobotAgentsConfigEditor';
import { RobotAgentsConfigDocument } from './RobotAgentsConfigDocument';
import { AGENT_CONFIG_FILE_NAME, getRobotAgents, SOLUTION_ROBOT_DIRECTORY } from './getRobotAgents';
import { ROBOT_ICON_SVG } from '../robotServiceType/PropertiesRobotTaskPane';

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
    () => {
      getRobotAgents(studio);
      studio.editors.focusOrOpenEditorDocument(studio.solution.getSolution()?.baseUri + SOLUTION_ROBOT_DIRECTORY +  AGENT_CONFIG_FILE_NAME);
    },
    () => studio.solution.hasOpenSolution(),
  );

  studio.editors.registerDocumentType('editor-document-robot-agents', {
    uriMatch: /\.processcube\/robot-agent\/agents\.json$/,
    rendererKey: 'RobotAgentsConfigEditor',
    rendererConstructor: RobotAgentsConfigEditor,
    modelKey: 'RobotAgentsConfigDocument',
    modelConstructor: RobotAgentsConfigDocument,
    icon: 'robot-framework-icon'
  });

  studio.icons.registerIcons({ 'robot-framework-icon': ROBOT_ICON_SVG });
}
