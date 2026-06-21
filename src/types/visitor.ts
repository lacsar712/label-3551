export type VisitorStatus = 'visiting' | 'left'

export interface Visitor {
  id: number
  name: string
  phone: string
  idCardLast4: string
  ownerName: string
  unitName: string
  visitReason: string
  estimatedDuration: number
  estimatedLeaveTime: string
  actualLeaveTime?: string
  status: VisitorStatus
  registerTime: string
  registerStaff?: string
}

export interface VisitorFilter {
  visitDate?: string
  ownerId?: string
  status?: VisitorStatus | ''
}
