"use client"

import * as React from "react"
import { Loader2, CheckCircle2, XCircle } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { CLICommand, CommandField } from "@/lib/cli-commands"

interface CommandDialogProps {
  command: CLICommand | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onExecute: (command: CLICommand, data: any) => Promise<any>
}

export function CommandDialog({ command, open, onOpenChange, onExecute }: CommandDialogProps) {
  const [currentStep, setCurrentStep] = React.useState(0)
  const [isExecuting, setIsExecuting] = React.useState(false)
  const [executionResult, setExecutionResult] = React.useState<any>(null)
  const [formData, setFormData] = React.useState<Record<string, any>>({})

  const useSheetLayout = command?.steps && command.steps.length > 1

  React.useEffect(() => {
    if (!open) {
      setCurrentStep(0)
      setIsExecuting(false)
      setExecutionResult(null)
      setFormData({})
    }
  }, [open])

  if (!command) return null

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }))
  }

  const handleNext = () => {
    if (command.steps && currentStep < command.steps.length - 1) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      const result = await onExecute(command, formData)
      setExecutionResult(result)
    } catch (error: any) {
      setExecutionResult({ status: "failed", error: error.message })
    } finally {
      setIsExecuting(false)
    }
  }

  const renderField = (field: CommandField) => {
    const value = formData[field.name] ?? field.defaultValue ?? ""

    switch (field.type) {
      case "textarea":
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Textarea
              id={field.name}
              placeholder={field.placeholder}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              rows={4}
            />
            {field.helpText && (
              <p className="text-xs text-muted-foreground">{field.helpText}</p>
            )}
          </div>
        )

      case "select":
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Select
              value={value}
              onValueChange={(val) => handleFieldChange(field.name, val)}
            >
              <SelectTrigger>
                <SelectValue placeholder={field.placeholder} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {field.helpText && (
              <p className="text-xs text-muted-foreground">{field.helpText}</p>
            )}
          </div>
        )

      case "checkbox":
        return (
          <div key={field.name} className="flex items-center space-x-2">
            <Checkbox
              id={field.name}
              checked={value}
              onCheckedChange={(checked) => handleFieldChange(field.name, checked)}
            />
            <Label htmlFor={field.name} className="cursor-pointer">
              {field.label}
            </Label>
          </div>
        )

      case "number":
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Input
              id={field.name}
              type="number"
              placeholder={field.placeholder}
              value={value}
              onChange={(e) => handleFieldChange(field.name, parseInt(e.target.value))}
            />
            {field.helpText && (
              <p className="text-xs text-muted-foreground">{field.helpText}</p>
            )}
          </div>
        )

      default:
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Input
              id={field.name}
              type="text"
              placeholder={field.placeholder}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
            />
            {field.helpText && (
              <p className="text-xs text-muted-foreground">{field.helpText}</p>
            )}
          </div>
        )
    }
  }

  const renderStepContent = () => {
    if (!command.steps || command.steps.length === 0) {
      return (
        <div className="py-8 text-center text-muted-foreground">
          <p>This command doesn't require any input.</p>
          <p className="text-sm mt-2">Click Execute to run the command.</p>
        </div>
      )
    }

    const step = command.steps[currentStep]

    return (
      <div className="space-y-4">
        {step.description && (
          <p className="text-sm text-muted-foreground">{step.description}</p>
        )}
        {step.fields.map(renderField)}
      </div>
    )
  }

  const renderResult = () => {
    if (!executionResult) return null

    const isSuccess = executionResult.status === "success" || executionResult.status === "deployed"
    const Icon = isSuccess ? CheckCircle2 : XCircle

    return (
      <div className="space-y-4">
        <div className={`flex items-center gap-2 ${isSuccess ? "text-green-600" : "text-red-600"}`}>
          <Icon className="h-5 w-5" />
          <span className="font-medium">
            {isSuccess ? "Command executed successfully!" : "Command failed"}
          </span>
        </div>

        {executionResult.error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">{executionResult.error}</p>
          </div>
        )}

        {executionResult.generated_contract_code && (
          <div className="space-y-2">
            <Label>Generated Contract</Label>
            <ScrollArea className="h-[200px] w-full rounded-md border p-4">
              <pre className="text-xs">
                <code>{executionResult.generated_contract_code}</code>
              </pre>
            </ScrollArea>
          </div>
        )}

        {executionResult.project_dir && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Project Directory:</strong> {executionResult.project_dir}
            </p>
          </div>
        )}

        {executionResult.transaction_id && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-800">
              <strong>Transaction ID:</strong> {executionResult.transaction_id}
            </p>
          </div>
        )}
      </div>
    )
  }

  const content = (
    <>
      {isExecuting ? (
        <div className="py-8 space-y-4">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
          <p className="text-center text-sm text-muted-foreground">
            Executing command...
          </p>
          <Progress value={undefined} className="w-full" />
        </div>
      ) : executionResult ? (
        renderResult()
      ) : (
        renderStepContent()
      )}
    </>
  )

  const footer = !executionResult && (
    <DialogFooter>
      {command.steps && command.steps.length > 1 && currentStep > 0 && (
        <Button variant="outline" onClick={handleBack} disabled={isExecuting}>
          Back
        </Button>
      )}
      {command.steps && currentStep < command.steps.length - 1 ? (
        <Button onClick={handleNext} disabled={isExecuting}>
          Next
        </Button>
      ) : (
        <Button onClick={handleExecute} disabled={isExecuting}>
          {isExecuting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Executing...
            </>
          ) : (
            "Execute"
          )}
        </Button>
      )}
    </DialogFooter>
  )

  if (useSheetLayout) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-full sm:max-w-2xl">
          <SheetHeader>
            <SheetTitle>{command.name}</SheetTitle>
            <SheetDescription>{command.description}</SheetDescription>
            {command.steps && command.steps.length > 1 && (
              <div className="flex items-center gap-2 pt-2">
                {command.steps.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-2 flex-1 rounded-full ${
                      idx <= currentStep ? "bg-primary" : "bg-muted"
                    }`}
                  />
                ))}
              </div>
            )}
          </SheetHeader>
          <div className="mt-6">{content}</div>
          {footer && <div className="mt-6">{footer}</div>}
        </SheetContent>
      </Sheet>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{command.name}</DialogTitle>
          <DialogDescription>{command.description}</DialogDescription>
        </DialogHeader>
        {content}
        {footer}
      </DialogContent>
    </Dialog>
  )
}
