import type { Visitor, OwnerOption, UnitOption } from '../types/visitor'

export const mockOwners: OwnerOption[] = [
  { id: 1, username: 'owner1', name: '业主张三' },
  { id: 2, username: 'owner2', name: '业主李四' },
  { id: 3, username: 'owner3', name: '业主王五' },
]

export const mockUnits: UnitOption[] = [
  { id: 1, ownerId: 1, name: '翠湖天地-1栋-101室' },
  { id: 2, ownerId: 1, name: '翠湖天地-2栋-302室' },
  { id: 3, ownerId: 2, name: '翠湖天地-1栋-102室' },
  { id: 4, ownerId: 3, name: '翠湖天地-3栋-501室' },
  { id: 5, ownerId: 3, name: '翠湖天地-3栋-502室' },
]

export const mockVisitors: Visitor[] = [
  {
    id: 1,
    name: '张三',
    phone: '13812345678',
    idCardLast4: '1234',
    ownerName: 'owner1',
    unitName: '翠湖天地-1栋-101室',
    visitReason: '亲友拜访',
    estimatedDuration: 120,
    estimatedLeaveTime: '2026-06-21 18:00',
    status: 'visiting',
    registerTime: '2026-06-21 16:00',
    registerStaff: 'staff',
  },
  {
    id: 2,
    name: '李四',
    phone: '13987654321',
    idCardLast4: '5678',
    ownerName: 'owner2',
    unitName: '翠湖天地-1栋-102室',
    visitReason: '快递配送',
    estimatedDuration: 30,
    estimatedLeaveTime: '2026-06-21 17:00',
    status: 'visiting',
    registerTime: '2026-06-21 16:30',
    registerStaff: 'staff',
  },
  {
    id: 3,
    name: '王五',
    phone: '13611112222',
    idCardLast4: '9012',
    ownerName: 'owner1',
    unitName: '翠湖天地-1栋-101室',
    visitReason: '家政服务',
    estimatedDuration: 180,
    estimatedLeaveTime: '2026-06-21 19:00',
    actualLeaveTime: '2026-06-21 18:30',
    status: 'left',
    registerTime: '2026-06-21 15:00',
    registerStaff: 'staff',
  },
]
