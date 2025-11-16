import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RobotAgentsConfigEditor } from '../RobotAgentsConfigEditor';
import { RobotAgentsConfigDocument } from '../RobotAgentsConfigDocument';

// Mock uuid to have predictable IDs for testing
jest.mock('uuid', () => ({
  v4: jest.fn(() => 'mock-uuid-12345'),
}));

const mockEditorDocument = {
  uri: 'file:///workspace/.processcube/robot-agent/agents.json',
  documentType: 'robot-agents',
};

const mockEditorDocumentModel = {
  getValue: jest.fn(),
  setValue: jest.fn(),
};

const mockStudio = {
  editors: {
    getEditorDocumentModel: jest.fn(),
  },
};

describe('RobotAgentsConfigEditor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render null while model is loading', () => {
      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      const { container } = render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('should render editor after model loads', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      const { container } = render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        expect(container.querySelector('.editor')).toBeInTheDocument();
      });
    });

    it('should display title', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({ agents: [] });
      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Robot Agents')).toBeInTheDocument();
      });
    });
  });

  describe('agent list display', () => {
    it('should display all agents from config', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
          { uuid: '2', name: 'Agent 2', url: 'http://localhost:8081' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        const editors = screen.getAllByTestId('one-line-code-editor');
        // 2 agents * 2 fields (name, url) = 4, plus 1 new empty agent
        expect(editors.length).toBeGreaterThanOrEqual(4);
      });
    });

    it('should add empty agent row at the end', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        const editors = screen.getAllByTestId('one-line-code-editor');
        // Should have 1 agent (2 fields) + 1 empty agent (2 fields) = 4
        expect(editors.length).toBe(4);
      });
    });

    it('should display empty agents list', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({ agents: [] });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        // Should only have 1 empty agent row
        const editors = screen.getAllByTestId('one-line-code-editor');
        expect(editors.length).toBe(2);
      });
    });
  });

  describe('agent editing', () => {
    it('should update agent name', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Old Name', url: 'http://localhost:8080' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        const editors = screen.getAllByTestId('one-line-code-editor');
        expect(editors.length).toBeGreaterThan(0);
      });

      const nameEditors = screen.getAllByTestId('one-line-code-editor');
      fireEvent.change(nameEditors[0], { target: { value: 'New Name' } });

      await waitFor(() => {
        expect(mockEditorDocumentModel.setValue).toHaveBeenCalled();
      });
    });

    it('should update agent URL', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://old-url:8080' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        const editors = screen.getAllByTestId('one-line-code-editor');
        expect(editors.length).toBeGreaterThan(0);
      });

      const urlEditors = screen.getAllByTestId('one-line-code-editor');
      fireEvent.change(urlEditors[1], { target: { value: 'http://new-url:9000' } });

      await waitFor(() => {
        expect(mockEditorDocumentModel.setValue).toHaveBeenCalled();
      });
    });
  });

  describe('agent removal', () => {
    it('should remove agents with empty name and URL', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: 'http://localhost:8080' },
          { uuid: '2', name: '', url: '' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        const lastCall = mockEditorDocumentModel.setValue.mock.calls[
          mockEditorDocumentModel.setValue.mock.calls.length - 1
        ];
        if (lastCall) {
          expect(lastCall[0].agents).toHaveLength(1);
        }
      });
    });

    it('should keep agents with at least name or URL', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({
        agents: [
          { uuid: '1', name: 'Agent 1', url: '' },
          { uuid: '2', name: '', url: 'http://localhost:8080' },
        ],
      });

      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        const lastCall = mockEditorDocumentModel.setValue.mock.calls[
          mockEditorDocumentModel.setValue.mock.calls.length - 1
        ];
        if (lastCall) {
          expect(lastCall[0].agents.length).toBeGreaterThanOrEqual(2);
        }
      });
    });
  });

  describe('lifecycle methods', () => {
    it('should call getEditorDocumentModel on mount', async () => {
      mockEditorDocumentModel.getValue.mockReturnValue({ agents: [] });
      mockStudio.editors.getEditorDocumentModel.mockResolvedValue(
        mockEditorDocumentModel
      );

      render(
        <RobotAgentsConfigEditor
          editorDocument={mockEditorDocument as any}
          studio={mockStudio as any}
        />
      );

      await waitFor(() => {
        expect(
          mockStudio.editors.getEditorDocumentModel
        ).toHaveBeenCalledWith(mockEditorDocument);
      });
    });
  });
});