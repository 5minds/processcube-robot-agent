import { initializeServiceTaskTypeRobot } from '../robotServiceType/initializeServiceTypeRobot';
import { initializeAgentSettingsEditor } from '../agentSettings/initializeAgentSettingsEditor';

describe('Studio Extension Integration', () => {
  describe('initializeServiceTaskTypeRobot', () => {
    it('should register help text for robot service task', () => {
      const mockStudio = {
        helpTexts: {
          registerHelpText: jest.fn(),
        },
        panes: {
          insertInPaneGroupAfter: jest.fn(),
          getPaneViaPaneProvider: jest.fn(),
        },
        commands: {
          executeCommand: jest.fn(),
        },
      } as any;

      initializeServiceTaskTypeRobot(mockStudio);

      expect(mockStudio.helpTexts.registerHelpText).toHaveBeenCalledWith(
        'bpmn/properties/robot_service_task',
        expect.any(String)
      );
    });

    it('should insert robot properties pane after service task pane', () => {
      const mockStudio = {
        helpTexts: {
          registerHelpText: jest.fn(),
        },
        panes: {
          insertInPaneGroupAfter: jest.fn(),
          getPaneViaPaneProvider: jest.fn(),
        },
        commands: {
          executeCommand: jest.fn(),
        },
      } as any;

      initializeServiceTaskTypeRobot(mockStudio);

      expect(mockStudio.panes.insertInPaneGroupAfter).toHaveBeenCalledWith(
        'right',
        'property',
        'bpmn/panes/properties/PropertiesServiceTask',
        expect.any(Array)
      );
    });

    it('should register internal robot agent property', () => {
      const mockStudio = {
        helpTexts: {
          registerHelpText: jest.fn(),
        },
        panes: {
          insertInPaneGroupAfter: jest.fn(),
          getPaneViaPaneProvider: jest.fn(),
        },
        commands: {
          executeCommand: jest.fn(),
        },
      } as any;

      initializeServiceTaskTypeRobot(mockStudio);

      const calls = mockStudio.commands.executeCommand.mock.calls;
      expect(calls).toContainEqual([
        'bpmn.customProperties.registerInternalProperty',
        expect.arrayContaining([
          'ExternalServiceTask',
          'studio.externalTask.robotAddin.agentId',
        ]),
      ]);
    });

    it('should register robot custom type for external tasks', () => {
      const mockStudio = {
        helpTexts: {
          registerHelpText: jest.fn(),
        },
        panes: {
          insertInPaneGroupAfter: jest.fn(),
          getPaneViaPaneProvider: jest.fn(),
        },
        commands: {
          executeCommand: jest.fn(),
        },
      } as any;

      initializeServiceTaskTypeRobot(mockStudio);

      const calls = mockStudio.commands.executeCommand.mock.calls;
      expect(calls).toContainEqual([
        'bpmn.externalTasks.registerCustomType',
        [{ type: 'robot', label: 'Robot' }],
      ]);
    });
  });

  describe('initializeAgentSettingsEditor', () => {
    it('should register configure robot agents menu item', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(),
          hasOpenSolution: jest.fn(() => true),
        },
      } as any;

      initializeAgentSettingsEditor(mockStudio);

      expect(mockStudio.menus.registerMenuModifier).toHaveBeenCalled();
    });

    it('should register robot agents command', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
          focusOrOpenEditorDocument: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(() => ({
            baseUri: 'file:///workspace',
          })),
          hasOpenSolution: jest.fn(() => true),
        },
      } as any;

      initializeAgentSettingsEditor(mockStudio);

      expect(mockStudio.commands.registerInCommandSearch).toHaveBeenCalledWith(
        'plugin.robot-agents.editAgents',
        'Robot Agents: Configure Agents',
        expect.any(Function),
        expect.any(Function)
      );
    });

    it('should register robot framework icon', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(),
          hasOpenSolution: jest.fn(() => true),
        },
      } as any;

      initializeAgentSettingsEditor(mockStudio);

      expect(mockStudio.icons.registerIcons).toHaveBeenCalledWith(
        { 'robot-framework-icon': expect.any(Object) }
      );
    });

    it('should register robot agents document editor', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(),
          hasOpenSolution: jest.fn(() => true),
        },
      } as any;

      initializeAgentSettingsEditor(mockStudio);

      expect(mockStudio.editors.registerDocumentType).toHaveBeenCalledWith(
        'editor-document-robot-agents',
        expect.objectContaining({
          uriMatch: expect.any(RegExp),
          rendererKey: 'RobotAgentsConfigEditor',
          rendererConstructor: expect.any(Function),
          modelKey: 'RobotAgentsConfigDocument',
          modelConstructor: expect.any(Function),
          icon: 'robot-framework-icon',
        })
      );
    });

    it('should register document type with correct URI pattern', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(),
          hasOpenSolution: jest.fn(() => true),
        },
      } as any;

      initializeAgentSettingsEditor(mockStudio);

      const call = mockStudio.editors.registerDocumentType.mock.calls[0];
      const config = call[1];

      // Test the regex pattern
      expect(config.uriMatch.test('.processcube/robot-agent/agents.json')).toBe(true);
      expect(config.uriMatch.test('.processcube/robot-agent/other.json')).toBe(false);
      expect(config.uriMatch.test('agents.json')).toBe(false);
    });
  });

  describe('command execution in settings', () => {
    it('should open agent settings editor when command is executed', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
          focusOrOpenEditorDocument: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(() => ({
            baseUri: 'file:///workspace',
          })),
          hasOpenSolution: jest.fn(() => true),
        },
        files: {
          watchFile: jest.fn(() => ({} as any)),
          getLocalFilenameForUri: jest.fn(),
          getUriForFilename: jest.fn(),
        },
      } as any;

      mockStudio.files.getLocalFilenameForUri.mockReturnValue('/.processcube/robot-agent/');
      require('fs').existsSync = jest.fn(() => true);
      require('fs').readFileSync = jest.fn(() => JSON.stringify({ agents: [] }));

      initializeAgentSettingsEditor(mockStudio);

      const commandHandler = mockStudio.commands.registerInCommandSearch.mock.calls[0][2];
      commandHandler();

      expect(mockStudio.editors.focusOrOpenEditorDocument).toHaveBeenCalledWith(
        expect.stringContaining('agents.json')
      );
    });

    it('should check if solution is open before executing command', () => {
      const mockStudio = {
        menus: {
          registerMenuModifier: jest.fn(),
          appendToMenu: jest.fn(),
        },
        commands: {
          registerInCommandSearch: jest.fn(),
        },
        icons: {
          registerIcons: jest.fn(),
        },
        editors: {
          registerDocumentType: jest.fn(),
        },
        solution: {
          getSolution: jest.fn(),
          hasOpenSolution: jest.fn(() => false),
        },
      } as any;

      initializeAgentSettingsEditor(mockStudio);

      const condition = mockStudio.commands.registerInCommandSearch.mock.calls[0][3];

      expect(condition()).toBe(false);
    });
  });
});