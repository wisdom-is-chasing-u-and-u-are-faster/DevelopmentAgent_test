import { Request, Response } from 'express';
import { pool } from '../../db/client';
import { formatRFC7807Error } from '../validators/ticket.validator';

export class SettingsController {
  public static async getActiveSettings(req: Request, res: Response) {
    try {
      const themeRes = await pool.query(
        `SELECT * FROM ui_presets WHERE preset_type = 'THEME_COLOR' ORDER BY is_global_default DESC, updated_at DESC LIMIT 1`
      );
      const layoutRes = await pool.query(
        `SELECT * FROM ui_presets WHERE preset_type = 'WORKLIST_LAYOUT' ORDER BY is_global_default DESC, updated_at DESC LIMIT 1`
      );

      const formatPreset = (row: any) => {
        if (!row) return null;
        let config = row.config_json;
        if (typeof config === 'string') {
          try { config = JSON.parse(config); } catch (e) { config = {}; }
        }
        return {
          id: row.id,
          preset_type: row.preset_type,
          name: row.name,
          config,
          is_global_default: Boolean(row.is_global_default),
          created_by: row.created_by,
          created_at: row.created_at,
          updated_at: row.updated_at
        };
      };

      return res.status(200).json({
        theme: formatPreset(themeRes.rows[0]),
        worklist_layout: formatPreset(layoutRes.rows[0])
      });
    } catch (err: any) {
      console.error('Error in getActiveSettings:', err);
      return res.status(500).json(formatRFC7807Error(500, 'Settings Error', err.message));
    }
  }

  public static async listPresets(req: Request, res: Response) {
    try {
      const { preset_type } = req.query;
      let queryText = 'SELECT * FROM ui_presets WHERE 1=1';
      const params: any[] = [];

      if (preset_type) {
        queryText += ' AND preset_type = $1';
        params.push(preset_type);
      }
      queryText += ' ORDER BY preset_type ASC, is_global_default DESC, name ASC';

      const result = await pool.query(queryText, params);
      const presets = result.rows.map((row: any) => {
        let config = row.config_json;
        if (typeof config === 'string') {
          try { config = JSON.parse(config); } catch (e) { config = {}; }
        }
        return {
          id: row.id,
          preset_type: row.preset_type,
          name: row.name,
          config,
          is_global_default: Boolean(row.is_global_default),
          created_by: row.created_by,
          created_at: row.created_at,
          updated_at: row.updated_at
        };
      });

      return res.status(200).json({ presets, total: presets.length });
    } catch (err: any) {
      console.error('Error in listPresets:', err);
      return res.status(500).json(formatRFC7807Error(500, 'Settings Error', err.message));
    }
  }

  public static async createPreset(req: Request, res: Response) {
    try {
      const { preset_type, name, config, is_global_default } = req.body;
      if (!preset_type || !name || !config) {
        return res.status(400).json(formatRFC7807Error(400, 'Validation Error', 'preset_type, name, and config are required'));
      }

      const presetId = `preset-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`;
      const isGlobal = Boolean(is_global_default);

      if (isGlobal) {
        await pool.query('UPDATE ui_presets SET is_global_default = FALSE WHERE preset_type = $1', [preset_type]);
      }

      const configJson = typeof config === 'string' ? config : JSON.stringify(config);
      const insertRes = await pool.query(
        `INSERT INTO ui_presets (id, preset_type, name, config_json, is_global_default, created_by)
         VALUES ($1, $2, $3, $4, $5, $6)
         RETURNING *`,
        [presetId, preset_type, name, configJson, isGlobal, 'global-admin']
      );

      const row = insertRes.rows[0];
      return res.status(201).json({
        id: row.id,
        preset_type: row.preset_type,
        name: row.name,
        config: typeof row.config_json === 'string' ? JSON.parse(row.config_json) : row.config_json,
        is_global_default: Boolean(row.is_global_default),
        created_by: row.created_by,
        created_at: row.created_at,
        updated_at: row.updated_at
      });
    } catch (err: any) {
      console.error('Error in createPreset:', err);
      return res.status(500).json(formatRFC7807Error(500, 'Settings Error', err.message));
    }
  }

  public static async applyGlobalPreset(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const findRes = await pool.query('SELECT * FROM ui_presets WHERE id = $1', [id]);
      if (findRes.rows.length === 0) {
        return res.status(404).json(formatRFC7807Error(404, 'Not Found', `Preset ${id} not found`));
      }

      const preset = findRes.rows[0];
      await pool.query('UPDATE ui_presets SET is_global_default = FALSE WHERE preset_type = $1', [preset.preset_type]);
      const updateRes = await pool.query(
        'UPDATE ui_presets SET is_global_default = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = $1 RETURNING *',
        [id]
      );

      const row = updateRes.rows[0];
      return res.status(200).json({
        status: 'SUCCESS',
        message: `Preset '${row.name}' transferred and activated globally for all users.`,
        preset: {
          id: row.id,
          preset_type: row.preset_type,
          name: row.name,
          config: typeof row.config_json === 'string' ? JSON.parse(row.config_json) : row.config_json,
          is_global_default: true,
          created_by: row.created_by,
          created_at: row.created_at,
          updated_at: row.updated_at
        }
      });
    } catch (err: any) {
      console.error('Error in applyGlobalPreset:', err);
      return res.status(500).json(formatRFC7807Error(500, 'Settings Error', err.message));
    }
  }
}
