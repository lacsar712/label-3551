import { View, Text, Input, Picker } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useMemo } from 'react'
import styles from './index.module.scss'
import { mockOwners, mockUnits } from '@/data/mockVisitor'
import type { OwnerOption, UnitOption } from '@/types/visitor'
import { getTodayDateString } from '@/utils'

export default function VisitorAddPage() {
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [idCardLast4, setIdCardLast4] = useState('')
  const [visitReason, setVisitReason] = useState('')
  const [estimatedDuration, setEstimatedDuration] = useState('120')
  const [estimatedLeaveDate, setEstimatedLeaveDate] = useState(getTodayDateString())
  const [estimatedLeaveTime, setEstimatedLeaveTime] = useState('18:00')

  const [ownerIndex, setOwnerIndex] = useState<number>(-1)
  const [unitIndex, setUnitIndex] = useState<number>(-1)

  const ownerOptions = useMemo(() => mockOwners.map(o => o.name), [])

  const filteredUnits: UnitOption[] = useMemo(() => {
    if (ownerIndex < 0) return []
    const selectedOwner = mockOwners[ownerIndex]
    return mockUnits.filter(u => u.ownerId === selectedOwner.id)
  }, [ownerIndex])

  const unitOptions = useMemo(() => filteredUnits.map(u => u.name), [filteredUnits])

  const handleOwnerChange = (e: any) => {
    const newIndex = Number(e.detail.value)
    setOwnerIndex(newIndex)
    setUnitIndex(-1)
  }

  const handleUnitChange = (e: any) => {
    setUnitIndex(Number(e.detail.value))
  }

  const validatePhone = (phone: string): boolean => {
    return /^1[3-9]\d{9}$/.test(phone)
  }

  const validateIdCardLast4 = (value: string): boolean => {
    return /^\d{4}$/.test(value)
  }

  const handleSubmit = () => {
    if (!name.trim()) {
      Taro.showToast({ title: '请输入访客姓名', icon: 'none' })
      return
    }
    if (!phone || !validatePhone(phone)) {
      Taro.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!idCardLast4 || !validateIdCardLast4(idCardLast4)) {
      Taro.showToast({ title: '请输入正确的身份证后四位', icon: 'none' })
      return
    }
    if (ownerIndex < 0) {
      Taro.showToast({ title: '请选择拜访业主', icon: 'none' })
      return
    }
    if (unitIndex < 0) {
      Taro.showToast({ title: '请选择关联房号', icon: 'none' })
      return
    }
    if (!visitReason.trim()) {
      Taro.showToast({ title: '请输入来访事由', icon: 'none' })
      return
    }
    if (!estimatedDuration || Number(estimatedDuration) <= 0) {
      Taro.showToast({ title: '请输入正确的预计停留时长', icon: 'none' })
      return
    }

    const selectedOwner = mockOwners[ownerIndex]
    const selectedUnit = filteredUnits[unitIndex]

    if (selectedUnit.ownerId !== selectedOwner.id) {
      Taro.showToast({ title: '房号与业主不匹配，请重新选择', icon: 'none' })
      return
    }

    Taro.showModal({
      title: '确认提交',
      content: `访客：${name}\n拜访业主：${selectedOwner.name}\n房号：${selectedUnit.name}`,
      success: (res) => {
        if (res.confirm) {
          Taro.showToast({ title: '访客登记成功', icon: 'success' })
          setTimeout(() => Taro.navigateBack(), 800)
        }
      }
    })
  }

  return (
    <View className={styles.page}>
      <Text className={styles.title}>访客登记</Text>
      <View className={styles.form}>
        <View className={styles.field}>
          <Text className={styles.label}>访客姓名 <Text className={styles.required}>*</Text></Text>
          <Input 
            className={styles.input} 
            value={name} 
            onInput={(e) => setName(e.detail.value)} 
            placeholder="请输入访客姓名" 
            maxlength={50}
          />
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>联系电话 <Text className={styles.required}>*</Text></Text>
          <Input 
            className={styles.input} 
            value={phone} 
            onInput={(e) => setPhone(e.detail.value)} 
            placeholder="请输入联系电话" 
            type="number"
            maxlength={11}
          />
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>身份证后四位 <Text className={styles.required}>*</Text></Text>
          <Input 
            className={styles.input} 
            value={idCardLast4} 
            onInput={(e) => setIdCardLast4(e.detail.value)} 
            placeholder="请输入身份证后四位" 
            type="number"
            maxlength={4}
          />
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>拜访业主 <Text className={styles.required}>*</Text></Text>
          <Picker 
            mode='selector' 
            range={ownerOptions} 
            value={ownerIndex} 
            onChange={handleOwnerChange}
          >
            <View className={styles.picker}>
              <Text className={ownerIndex >= 0 ? styles.pickerText : styles.pickerPlaceholder}>
                {ownerIndex >= 0 ? ownerOptions[ownerIndex] : '请选择拜访业主'}
              </Text>
              <Text className={styles.pickerArrow}>›</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>关联房号 <Text className={styles.required}>*</Text></Text>
          <Picker 
            mode='selector' 
            range={unitOptions} 
            value={unitIndex} 
            onChange={handleUnitChange}
            disabled={ownerIndex < 0}
          >
            <View className={`${styles.picker} ${ownerIndex < 0 ? styles.pickerDisabled : ''}`}>
              <Text className={unitIndex >= 0 ? styles.pickerText : styles.pickerPlaceholder}>
                {ownerIndex < 0 
                  ? '请先选择拜访业主' 
                  : unitIndex >= 0 
                    ? unitOptions[unitIndex] 
                    : filteredUnits.length > 0 
                      ? '请选择关联房号' 
                      : '该业主名下暂无房产'}
              </Text>
              <Text className={styles.pickerArrow}>›</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>来访事由 <Text className={styles.required}>*</Text></Text>
          <Input 
            className={styles.input} 
            value={visitReason} 
            onInput={(e) => setVisitReason(e.detail.value)} 
            placeholder="请输入来访事由" 
            maxlength={200}
          />
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>预计停留时长(分钟) <Text className={styles.required}>*</Text></Text>
          <Input 
            className={styles.input} 
            value={estimatedDuration} 
            onInput={(e) => setEstimatedDuration(e.detail.value)} 
            placeholder="请输入预计停留时长" 
            type="number"
            min={1}
          />
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>预计离开日期 <Text className={styles.required}>*</Text></Text>
          <Picker 
            mode='date' 
            value={estimatedLeaveDate} 
            onChange={(e) => setEstimatedLeaveDate(e.detail.value)}
          >
            <View className={styles.picker}>
              <Text className={styles.pickerText}>{estimatedLeaveDate}</Text>
              <Text className={styles.pickerArrow}>›</Text>
            </View>
          </Picker>
        </View>

        <View className={styles.field}>
          <Text className={styles.label}>预计离开时间 <Text className={styles.required}>*</Text></Text>
          <Picker 
            mode='time' 
            value={estimatedLeaveTime} 
            onChange={(e) => setEstimatedLeaveTime(e.detail.value)}
          >
            <View className={styles.picker}>
              <Text className={styles.pickerText}>{estimatedLeaveTime}</Text>
              <Text className={styles.pickerArrow}>›</Text>
            </View>
          </Picker>
        </View>

        <Text className={styles.submit} onClick={handleSubmit}>提交登记</Text>
      </View>
    </View>
  )
}
