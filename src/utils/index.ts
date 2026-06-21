import type { Visitor, VisitorFilter } from '../types/visitor'

export function filterVisitors(visitors: Visitor[], filters: VisitorFilter): Visitor[] {
  return visitors.filter((visitor) => {
    if (filters.status && visitor.status !== filters.status) {
      return false
    }
    if (filters.ownerId && visitor.ownerName !== filters.ownerId) {
      return false
    }
    if (filters.visitDate && !visitor.registerTime.startsWith(filters.visitDate)) {
      return false
    }
    return true
  })
}

export function formatVisitorStatus(status: Visitor['status']): string {
  return status === 'visiting' ? '在访' : '已离场'
}
