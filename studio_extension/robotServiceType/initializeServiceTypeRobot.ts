import { BpmnElementType, Studio } from '@atlas-engine/atlas_studio_sdk';
import { paneProvider } from './PropertiesRobotTaskPane';

export const ROBOT_AGENT_PROPERTY_NAME = 'studio.externalTask.robotAddin.agentId';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const propertiesRobotServiceTaskDoku = require('./PropertiesRobotServiceTask.md');

export function initializeServiceTaskTypeRobot(studio: Studio): void {
  studio.helpTexts.registerHelpText('bpmn/properties/robot_service_task', propertiesRobotServiceTaskDoku);

  studio.panes.insertInPaneGroupAfter('right', 'property', 'bpmn/panes/properties/PropertiesServiceTask', [
    studio.panes.getPaneViaPaneProvider(
      'bpmn/panes/properties/PropertiesExternalRobotTask',
      'bpmn/pane-providers/properties/PropertiesExternalRobotTask',
      { paneProvider },
    ),
  ]);

  studio.commands.executeCommand('bpmn.customProperties.registerInternalProperty', [
    BpmnElementType.ExternalServiceTask,
    ROBOT_AGENT_PROPERTY_NAME,
  ]);

  studio.commands.executeCommand('bpmn.externalTasks.registerCustomType', [
    { type: 'robot', label: 'Robot' },
  ]);
}
