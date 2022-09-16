import { Studio } from '@atlas-engine/atlas_studio_sdk';

export function initializeServiceTypeRobot(studio: Studio): void {
  studio.commands.executeCommand('bpmn.externalTasks.registerCustomType', [
    { type: 'robot', label: 'Robot' }
  ]);

  studio.panes.insertInPaneGroupAfter('right', 'property', 'bpmn/panes/properties/PropertiesServiceTask', [
    studio.panes.getPaneViaPaneProvider(
      'bpmn/panes/properties/PropertiesExternalRobotTask',
      'bpmn/pane-providers/properties/PropertiesExternalRobotTask',
      require('./PropertiesRobotTaskPane')
    ),
  ]);
}
