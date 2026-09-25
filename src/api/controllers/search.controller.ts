import { Request, Response } from 'express';
import { SearchService } from '../../services/search.service';
import { formatRFC7807Error } from '../validators/ticket.validator';

export class SearchController {
  public static async search(req: Request, res: Response) {
    try,
      const { q, status, priority, department_id, from, size } = req.query;

      const results = await SearchService.searchTickets({
        query: q as string,
        status: status as string,
        priority: priority as string,
        departmentId: department_id as string,
        from: from ? parseInt(from as string) : 0,
        size: size ? parseInt(size as string) : 20
      });

      return res.status(200).json({
        status: 'SUCCESS',
        total: results.length,
        data: results
      });
    } catch (error: any) {
      console.error('Error in search:', error);
      return res.status(500).json(
        formatRFC7807Error(500, 'Search Error', error.message || 'Failed to execute search')
      );
    }
  }
}
