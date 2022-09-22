import { BpmnElementType, Studio } from '@atlas-engine/atlas_studio_sdk';

export const ROBOT_AGENT_PROPERTY_NAME = 'studio.externalTask.robotAddin.agentId';

export function initializeServiceTaskTypeRobot(studio: Studio): void {
  studio.panes.insertInPaneGroupAfter('right', 'property', 'bpmn/panes/properties/PropertiesServiceTask', [
    studio.panes.getPaneViaPaneProvider(
      'bpmn/panes/properties/PropertiesExternalRobotTask',
      'bpmn/pane-providers/properties/PropertiesExternalRobotTask',
      require('./PropertiesRobotTaskPane')
    ),
  ]);

  studio.commands.executeCommand('bpmn.customProperties.registerInternalProperty', [
    BpmnElementType.ExternalServiceTask,
    ROBOT_AGENT_PROPERTY_NAME,
  ]);

  studio.commands.executeCommand('bpmn.externalTasks.registerCustomType', [
    { type: 'robot', label: 'Robot' }
  ]);
}
